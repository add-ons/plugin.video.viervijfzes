# Auth API

[vier.be](https://www.vier.be), [vijf.be](https://www.vijf.be) en [zestv.be](https://www.zestv.be) are using [Amazon Cognito](https://aws.amazon.com/cognito/) for authentication.

To authenticate, the following information is used together with your login credentials. You can create an account on one of the websites.

| Key       | Value                        |
|-----------|------------------------------|
| Region    | `eu-west-1`                  |
| Pool ID   | `eu-west-1_dViSsKM5Y`        |
| Client ID | `6s1h851s8uplco5h6mqh1jac8m` |

After authentication, we need to use the `IdToken` to authenticate our requests.