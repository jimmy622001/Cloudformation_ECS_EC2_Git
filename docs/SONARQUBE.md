# Using SonarQube Securely

## Security Issue Fixed

A SonarQube token was previously hardcoded in the `sonar-scanner.properties` file, which posed a security risk. This token has been removed from the codebase.

## How to Use SonarQube Scanner Securely

1. **Never commit tokens to the repository**
   - SonarQube tokens should be treated as sensitive credentials
   - The `sonar-scanner.properties` file is now added to `.gitignore`

2. **Use environment variables instead:**
   ```bash
   # Set the token as an environment variable
   export SONAR_TOKEN=your-new-token
   
   # Run the scanner
   sonar-scanner
   ```

3. **Alternatively, pass the token via command line:**
   ```bash
   sonar-scanner -Dsonar.login=your-new-token
   ```

4. **In CI/CD environments:**
   - Store the token as a secret in your CI/CD system (GitHub Secrets, Jenkins Credentials, etc.)
   - Reference the secret in your pipeline configuration

## Important

* The previously exposed token (`686f222f3fbac399424daef3ee19f05be94e1173`) should be considered compromised
* Generate a new token in your SonarQube/SonarCloud account
* Revoke the old token immediately

## References

* [SonarQube Scanner Documentation](https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/)
* [SonarQube Security Best Practices](https://docs.sonarqube.org/latest/instance-administration/security/)