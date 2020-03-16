# Auth API

[vier.be](https://www.vier.be), [vijf.be](https://www.vijf.be) en [zestv.be](https://www.zestv.be) are using [Amazon Cognito](https://aws.amazon.com/cognito/) for authentication.

To authenticate, the following information is used together with your login credentials. You can create an account on one of the websites.

| Key       | Value                        |
|-----------|------------------------------|
| Region    | `eu-west-1`                  |
| Pool ID   | `eu-west-1_dViSsKM5Y`        |
| Client ID | `6s1h851s8uplco5h6mqh1jac8m` |

You need to use the `Secure Remote Password (SRP)` protocol when authenticating. After authentication, the `IdToken` can be used to authenticate the requests.