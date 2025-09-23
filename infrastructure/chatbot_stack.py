"""CDK Stack for Chatbot API infrastructure."""

from typing import Dict, Any
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_cognito as cognito,
    aws_logs as logs,
    aws_iam as iam,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class ChatbotStack(Stack):
    """CDK Stack for serverless chatbot API."""

    def __init__(self, scope: Construct, construct_id: str, deploy_environment: str = "dev", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.deploy_environment = deploy_environment

        # Create S3 bucket for static assets
        self.assets_bucket = s3.Bucket(
            self,
            "AssetsBucket",
            bucket_name=f"chatbot-api-{self.deploy_environment}-assets-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # For dev/test
        )

        # Create Cognito User Pool
        self.user_pool = self._create_cognito_user_pool()

        # Create Lambda function
        self.lambda_function = self._create_lambda_function()

        # Create API Gateway
        self.api_gateway = self._create_api_gateway()

        # Create CloudFront distribution
        self.cloudfront_distribution = self._create_cloudfront_distribution()

        # Create outputs
        self._create_outputs()

    def _create_cognito_user_pool(self) -> cognito.UserPool:
        """Create Cognito User Pool for authentication."""
        user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=f"chatbot-api-{self.deploy_environment}-users",
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # For dev/test
        )

        # Add OAuth providers
        user_pool.add_domain(
            "Domain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"chatbot-api-{self.deploy_environment}-{self.account}"
            )
        )

        # Create user pool client
        user_pool_client = user_pool.add_client(
            "WebClient",
            user_pool_client_name=f"chatbot-{self.deploy_environment}-web-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            generate_secret=False,  # For web clients
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True,
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
                callback_urls=self._get_oauth_urls("callback"),
                logout_urls=self._get_oauth_urls("logout"),
            ),
        )

        # Store client ID for Lambda environment
        self.user_pool_client_id = user_pool_client.user_pool_client_id

        return user_pool

    def _create_lambda_function(self) -> lambda_.Function:
        """Create Lambda function for the API."""
        # Create execution role
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Add permissions for Cognito
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cognito-idp:AdminGetUser",
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminSetUserPassword",
                    "cognito-idp:AdminUpdateUserAttributes",
                ],
                resources=[self.user_pool.user_pool_arn],
            )
        )

        # Add permissions for Systems Manager Parameter Store
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath",
                ],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/chatbot-api/{self.deploy_environment}/*"
                ],
            )
        )

        # Create log group for Lambda function
        log_group = logs.LogGroup(
            self,
            "ChatbotApiLogGroup",
            log_group_name=f"/aws/lambda/chatbot-api-{self.deploy_environment}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create Lambda function
        lambda_function = lambda_.Function(
            self,
            "ChatbotApiFunction",
            function_name=f"chatbot-api-{self.deploy_environment}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_handler.lambda_handler",
            code=lambda_.Code.from_asset("../src"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                "DEBUG": "false",
                "LOG_LEVEL": "INFO",
                "APP_NAME": "Chatbot API",
                "HOST": "0.0.0.0",
                "PORT": "8000",
                "COGNITO_USER_POOL_ID": self.user_pool.user_pool_id,
                "COGNITO_CLIENT_ID": self.user_pool_client_id,
                "COGNITO_REGION": self.region,
                "AWS_LAMBDA_FUNCTION_NAME": f"chatbot-api-{self.deploy_environment}",  # Indicates Lambda env
                "ENVIRONMENT": self.deploy_environment,
            },
            log_group=log_group,
        )

        return lambda_function

    def _create_api_gateway(self) -> apigwv2.HttpApi:
        """Create API Gateway HTTP API."""
        # Create Cognito authorizer
        authorizer = apigwv2.CfnAuthorizer(
            self,
            "CognitoAuthorizer",
            api_id="",  # Will be set after API creation
            authorizer_type="JWT",
            identity_source=["$request.header.Authorization"],
            jwt_configuration=apigwv2.CfnAuthorizer.JWTConfigurationProperty(
                audience=[self.user_pool_client_id],
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool.user_pool_id}"
            ),
            name="CognitoJwtAuthorizer",
        )

        # Create HTTP API
        api = apigwv2.HttpApi(
            self,
            "ChatbotHttpApi",
            api_name=f"chatbot-api-{self.deploy_environment}",
            description="Chatbot API with Lambda integration",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=self._get_cors_origins(),
                allow_methods=[apigwv2.CorsHttpMethod.ANY],
                allow_headers=["*"],
                allow_credentials=True,
            ),
        )

        # Set API ID for authorizer
        authorizer.api_id = api.api_id

        # Create Lambda integration
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            self.lambda_function,
        )

        # Add routes
        # Health endpoints (no auth required)
        api.add_routes(
            path="/health/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=lambda_integration,
        )

        # Auth endpoints (no auth required)
        api.add_routes(
            path="/auth/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=lambda_integration,
        )

        # Root endpoint (no auth required)
        api.add_routes(
            path="/",
            methods=[apigwv2.HttpMethod.GET],
            integration=lambda_integration,
        )

        # API endpoints (auth required)
        api.add_routes(
            path="/v1/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=lambda_integration,
            authorizer=apigwv2.HttpRouteAuthorizer.from_cfn_authorizer(authorizer),
        )

        # Catch-all route for other paths
        api.add_routes(
            path="/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=lambda_integration,
        )

        return api

    def _create_cloudfront_distribution(self) -> cloudfront.Distribution:
        """Create CloudFront distribution for global edge caching."""
        # Create origin access control for S3
        origin_access_control = cloudfront.S3OriginAccessControl(
            self,
            "OAC",
            description="OAC for chatbot API assets",
        )

        # Create distribution
        distribution = cloudfront.Distribution(
            self,
            "ChatbotDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.HttpOrigin(
                    f"{self.api_gateway.api_id}.execute-api.{self.region}.amazonaws.com",
                    protocol_policy=cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,  # API responses
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
            ),
            additional_behaviors={
                "/static/*": cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(
                        self.assets_bucket,
                        origin_access_control=origin_access_control,
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                ),
            },
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # US/Europe only
            comment="Chatbot API CloudFront Distribution",
        )

        # Add bucket policy for CloudFront access
        self.assets_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                actions=["s3:GetObject"],
                resources=[f"{self.assets_bucket.bucket_arn}/*"],
                conditions={
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"
                    }
                },
            )
        )

        return distribution

    def _get_oauth_urls(self, endpoint: str) -> list[str]:
        """Get environment-specific OAuth URLs."""
        if self.deploy_environment == "prod":
            # Replace with your production domain
            return [f"https://your-domain.com/{endpoint}"]
        else:
            # Development environment
            return [f"http://localhost:3000/{endpoint}"]

    def _get_cors_origins(self) -> list[str]:
        """Get environment-specific CORS origins."""
        if self.deploy_environment == "prod":
            # Replace with your production domains
            return ["https://your-domain.com"]
        else:
            # Development environment - allow localhost
            return ["http://localhost:3000", "http://localhost:8000"]

    def _create_outputs(self) -> None:
        """Create CloudFormation outputs."""
        CfnOutput(
            self,
            "ApiUrl",
            value=f"https://{self.api_gateway.api_id}.execute-api.{self.region}.amazonaws.com",
            description="API Gateway URL",
        )

        CfnOutput(
            self,
            "CloudFrontUrl",
            value=f"https://{self.cloudfront_distribution.distribution_domain_name}",
            description="CloudFront Distribution URL",
        )

        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID",
        )

        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client_id,
            description="Cognito User Pool Client ID",
        )

        CfnOutput(
            self,
            "LambdaFunctionName",
            value=self.lambda_function.function_name,
            description="Lambda Function Name",
        )