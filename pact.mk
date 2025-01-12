GITHUB_ORG="SatelliteVu"
PACTICIPANT?=python-sdk
PACT_CLI?=docker run --rm -v $(PWD):$(PWD) -e PACT_BROKER_BASE_URL -e PACT_BROKER_TOKEN pactfoundation/pact-cli:latest

# Only deploy from main
ifeq ($(GIT_BRANCH),main)
	DEPLOY_TARGET=deploy
else
	DEPLOY_TARGET=no_deploy
endif

## ====================
## CI tasks
## ====================

publish_pacts:
	@echo "\n========== STAGE: publish pacts ==========\n"
	$(PACT_CLI) publish $(PWD)/pacts --consumer-app-version $(GIT_COMMIT) --branch $(GIT_BRANCH); \
    $(PACT_CLI) broker create-version-tag --tag $(GIT_BRANCH) --pacticipant $(PACTICIPANT) --version $(GIT_COMMIT) \

last_branch=$(shell gh api graphql -f query='query { \
            	repository(owner: "SatelliteVu", name: "satellitevu-client-python") { \
            		pullRequests(first: 1, orderBy: {field: UPDATED_AT, direction: DESC}, states: MERGED, baseRefName: "main") { \
            			nodes { \
            				headRefName \
            			} \
            		} \
            	} \
            }' --jq '.data.repository.pullRequests.nodes[0].headRefName')

## =====================
## Deploy tasks
## =====================

create_qa_environment:
	@"$(PACT_CLI)" broker create-environment --name qa --no-production

create_prod_environment:
	@"$(PACT_CLI)" broker create-environment --name production --production

can_i_deploy:
	@echo "\n========== STAGE: can-i-deploy? ==========\n"
	$(PACT_CLI) broker can-i-deploy \
	  --pacticipant $(PACTICIPANT) \
	  --version $(GIT_COMMIT) \
	  --to-environment $(ENVIRONMENT) \
	  --retry-while-unknown 6 \
	  --retry-interval 10

set_branch_and_tag_pact:
	@latest_branch=$(jq -r --arg v "$(last_branch)" '$v | @uri'); \
	latest_version=$$(curl -s -H "Authorization: Bearer $(PACT_BROKER_TOKEN)" \
		"$(PACT_BROKER_BASE_URL)/pacticipants/$(PACTICIPANT)/latest-version/$$latest_branch" | jq -r .number); \
	$(PACT_CLI) broker create-or-update-version --pacticipant $(PACTICIPANT) --version $$latest_version --tag $(VERSION) --branch $(GIT_BRANCH); \
	$(PACT_CLI) broker delete-branch --branch $(last_branch) --pacticipant $(PACTICIPANT)

record_release:
	@latest_branch=$(jq -r --arg v "$(last_branch)" '$v | @uri'); \
	latest_version=$$(curl -s -H "Authorization: Bearer $(PACT_BROKER_TOKEN)" \
		"$(PACT_BROKER_BASE_URL)/pacticipants/$(PACTICIPANT)/latest-version/$$latest_branch" | jq -r .number); \
	$(PACT_CLI) broker record-release --pacticipant $(PACTICIPANT) --version $$latest_version --environment $(ENVIRONMENT)
