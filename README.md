# RECON

Recon is a GitHub repository analyzer build to support seamless adoption of open source tools in organisations. It can analyze repositories just by using the git clone url. The analysis includes data and history about the repository from its inceptions to understand its maturity and reliability. The repository currently fetches all the release data and commits between successive releases to understand the type of commits(Adaptive, Corrective, Perfective) in each release. This data is visualized to provide on overview of the repository age and activity to comment upon its maturity. The tool will be shipped with the proposed analyzers on product release.

## About tagging from GitHub

It’s common practice to prefix your version names with the letter v. Some good tag names might be v1.0 or v2.3.4.
If the tag isn’t meant for production use, add a pre-release version after the version name. Some good pre-release versions might be v0.2-alpha or v5.9-beta.3.

## Usage

Clone the git-recon repository

```bash
git clone https://github.com/SaipranavK/oss-recon.git
```

Change directory to repository root

```bash
cd oss-recon
```

### Using docker

Build the image

```bash
docker build -t oss-recon .
```

Scan repositories with reports volume mounted to the image

```bash
docker run -it -v $PWD/analysis:/app/analysis oss-recon -r <https_repo_url>
```

Mount the compliance manifest to the image to enable complaince checking

```bash
docker run -it -v $PWD/analysis:/app/analysis -v $PWD/compliance.yaml:/app/compliance.yaml oss-recon -r <https_repo_url> --check-compliance /app/compliance.yaml
```

### Using source

Create python3.6 or + virtual environment

```bash
python -m venv pyenv
```

Activate the environment

```bash
source ./pyenv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install OWASP dependency checker

```bash
python driver_alt.py --resolve-owasp
```

Run analysis

```bash
python driver.py -r <repo_name>
```

Run with compliance check enabled. See resources/sample_compliance.yaml for example compliance manifest

```bash
python driver.py -r <https_repo_url> --check-compliance <compliance_yaml>
```

## List of analyzers

- [x] **Meta**
Meta analyzer returns brief information about the repository.

| Attribute | Description |
| -- | -- |
| Owner  | Name of the repository Owner  |
| Name | Name of the repository |
| Description | Description of the repository |
| Topics | Topics/Tags assigned to the repository by Owner|
| API URL | URL to make an API GET request for complete information on the repository from the GitHub API |

---

- [x]  **Portability**
Portability defines the capability of the tool to communicate or be integrated in other organization specific ecosystems.

| Attribute | Description |
| -- | -- |
| Programming Languages  | The languages used to build the tool in the repository  |

---

- [x] **Usability**
Usability reflects on the availability of documentation and forums around the repository to give complete information and understanding of the tool.

| Attribute | Description |
| -- | -- |
| Documentation | Check if the repository has documentation |
| Wikis | Check if the repository has Wiki enabled |
| Stack Exchange QAs | Numbers of questions posed with tags associated with the repository |

---

- [x] **Reliability**
Reliability investigates the factors affecting the trust on the tool.

| Attribute | Description |
| -- | -- |
| Age | Age of the repository |
| Status check context | Look for workflows and checks setup in the repository |
| Average time to release | The time taken by the community to release a new version of the tool |
| Last updated | When was the last commit in the repository |
| Issues | Number of open issues |
| Active/Recent releases | List of active/recent releases |
| Recent Commit activity | Commit activity graph |

---

- [x] **Quality**
Quality returns different performance and security metrics to estimate the quality of the tool.

| Attribute | Description |
| -- | -- |
| Maturity | Graph image of commit maturity |
| Maintenance | Graph image of commit classification |
| Security | Found CVE from mitre.org |
| Deep Security | Report from OWASP dependency checker |
| Potential vulnerabilities found | Count of vulnerabilities |

---

- [x] **GitHub community metrics**
GitHub community metrics are set of attributes that represent the strength of the community behind the repository.

| Attribute | Description |
| -- | -- |
| Forks | Number of networks  |
| Stars | Number of stargazers |
| Watchers | Number of watchers |
| GitHub Community Health | Community metrics score of GitHub |

---

- [x] **Legal**
Legal is concerned about the compliance to modify and use the tool.

| Attribute | Description |
| -- | -- |
| License Type | Type of License of the repository |
| Permissions | List of permissions for the repo |
| Conditions | List of conditions to use the repo |
| Limitations | List of limitations on the repo|
| License | License text |

---

- [x] **Compliance**
Compliance analyzer checks if the repo abides to the user's constraints

| Attribute | Description |
| -- | -- |
| License | Pass/Fail |
| Community | Pass/Fail |
| Security - Max CVSS Limit | Pass/Fail |
| Security - Max CVE count | Pass/Fail |
