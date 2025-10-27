# GitHub Branch Protection Configuration
# This file documents the recommended branch protection settings

## Branch Protection Rules for 'main' branch

### Required Status Checks
- **test (Python 3.11)** - Main test suite
- **pr-validation** - Pull request validation
- **build-check** - Build verification

### Protection Settings
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require pull request reviews before merging
- ✅ Require review from code owners
- ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ Restrict pushes that create files larger than 100MB

### Additional Settings
- ✅ Require linear history
- ✅ Include administrators
- ❌ Allow force pushes (disabled)
- ❌ Allow deletions (disabled)

## Workflow Permissions
- ✅ Allow GitHub Actions to create and approve pull requests
- ✅ Allow actions and reusable workflows

## Required Secrets (Optional)
For full functionality testing:
- `SMTP_HOST` - SMTP server hostname
- `SMTP_PORT` - SMTP server port
- `SMTP_USERNAME` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `SMTP_FROM_EMAIL` - From email address
- `OPENAI_API_KEY` - OpenAI API key for enhanced analysis
- `TEST_EMAIL` - Test email address

## Code Coverage Integration (Optional)
- Sign up for Codecov.io
- Connect repository
- Add `CODECOV_TOKEN` secret

## Development Workflow
1. Work on `dev` branch
2. Create PR from `dev` to `main`
3. CI/CD pipeline runs automatically
4. Required reviewers approve
5. Merge to `main` triggers release workflow
