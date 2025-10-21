# Operations Runbook

## Daily Checks

1. Review Brand Centre API health dashboards for latency or authorization errors.
2. Monitor workflow execution logs for repeated missing-information prompts which
   may indicate training needs for brief authors.
3. Confirm that generated campaign plans are archived in accordance with DNB's
   seven-year retention policy.

## Incident Response

- **Authentication failures**: Rotate API credentials in the Brand Centre and
  update deployment secrets. Confirm the `BrandCenterClient` receives new tokens.
- **Data quality issues**: Validate input briefs for required sections. Use the
  CLI prompts to gather missing fields before initiating campaigns.
- **Dependency updates**: Run `poetry update` in a staging environment and
  execute `poetry run pytest` prior to promoting changes to production.

## Knowledge Transfer

- Schedule quarterly workshops using this runbook as the agenda template.
- Provide sample briefs and guideline JSON files to new team members for
  hands-on walkthroughs of the workflow and CLI tooling.
