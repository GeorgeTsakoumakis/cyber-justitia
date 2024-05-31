# CSC2033_Team25_23-24

## Cyber Justitia

[![Super-Linter](https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24/actions/workflows/linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)
[![Tests](https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24/actions/workflows/test.yml/badge.svg)](https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24/blob/george/.github/workflows/test.yml)

### Team Members

- [Yanhao Bao](https://github.com/YanhaoBao)
- [Ziad El Krekshi](https://github.com/neuziad)
- [Ionut-Valeriu Facaeru](https://github.com/IanFacaeru) / [Alternate account](https://github.com/PiscotOficial)
- [Jonathan Muse](https://github.com/Musey21)
- [Ayesha Suleman](https://github.com/xayeshasulx)
- [Georgios Tsakoumakis](https://github.com/gtsakoumakis2004)

Names are listed in alphabetical order by last name.

### Project Description

Cyber Justitia is a web application designed to provide free and informal legal advice to users through its two main services: the AI chatbot, which can be used to ask legal questions and receive information suited to the users' needs, and the forums, allowing users to post their legal enquiries publicly and have real legal professionals respond with general advice. Inspired by the U.N. Sustainable Development Goal #10 (Reduced Inequalities), Cyber Justitia was designed to provide users the means to communicate their legal troubles and get started on sorting them out, pro bono. Cyber Justitia is **not** designed to replace proper legal counsel, instead it gives users way to seek options and enquire on some of the more verbose aspects of law. Designed in Django.

[Repository can be found here.](https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24)

### Installation Instructions

1. Clone the repository:

```bash
git clone https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24.git
```

2. Change into the project directory:

```bash
cd CSC2033_Team25_23-24
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the virtual environment:

```bash
source venv/bin/activate
```

Or on Windows:

```bash
.\venv\Scripts\activate
```

5. Install the project dependencies:

```bash
pip install -r requirements.txt
```

6. Create a project on Google Cloud and find the project ID and location. For example, project ID `my-project` and location `us-central1`
7. Create a `.env` file in the root directory of the project and add the following environment variables:

```bash
SECRET_KEY=your_secret_key
DEBUG=False
DB_NAME=postgresql_db_name
DB_USER=postgresql_user
DB_PASSWORD=postgresql_password
DB_HOST=postgresql_host
DB_PORT=5432
PROJECT_ID="your_gcloud_project_id"
LOCATION="your_gcloud_project_location"
GOOGLE_CLOUD_PROJECT="your_gcloud_project_id"
JSON_AUTH_DETAILS={insert_json_credential_key_here}
VM_IP="your_vm_instance_external_ip_here"
```

If you are running locally this project locally, you won't need to input a VM IP as this is added for production uses only. If you want to deploy the app, make sure the external IP of your hosted VM is added to your environment variables as shown above.

8. Run the following command to create a db migration:

```bash
python manage.py makemigrations
```

#### Google Cloud Setup

You will also need to set up a Google Cloud Project to access the Gemini Pro model.
First, you will need to install the Google Cloud CLI from [here](https://cloud.google.com/sdk/docs/install)
If you want others admins to also have access on their machine, you can add roles via IAM.
Once they have installed gcloud cli, been assigned their roles and they have accepted access rights, everyone must run the following command:

```bash
gcloud auth application-default login
```

### Running the Application

To run the application, execute the following command:

```bash
python manage.py runserver
```

If static assets are not being served, run the following command:

```bash
python manage.py collectstatic
```

### Testing Instructions

**NOTE:** Before running tests, if you are using PyCharm IDE, make sure that your installed version is at least 2023.3.2. If not, update your IDE to the latest version.

Before running coverage to test the application make sure to install it as a dependency with the following command:

```bash
pip install -r requirements.txt
```

To test all apps, run the following command:

```bash
coverage run manage.py test -v 2
```

The -v 2 specifies the level of verbosity. The higher the number, the more detailed the output.

If you want to test a specific app, run the following command:

```bash
coverage run manage.py test <app_name> -v 2
```

Replace `<app_name>` with the name of the app you want to test.

To view the coverage report, run the following command:

```bash
coverage report
```

To view the coverage report in HTML format, run the following command:

```bash
coverage html
```

This will generate a directory called `htmlcov` which contains the HTML files for the coverage report. Open the `index.html` file in a web browser to view the report.

### Building with Docker

A Dockerfile, docker-compose.yml, entrypoint and .dockerignore file have been provided for local app deployment, as no full-scale deployment has been planned for Cyber Justitia due to time constraints. The docker-compose.yml will build build containers for both the web application and the external database, allowing for seemless communication between the two.

To begin, make sure that the Docker daemon is running and you are signed in to Docker Hub by running the following command:

```bash
docker login
```

Follow the instructions and input your credentials.

If you've done that or are already logged in, you can now build the application. In order to build and run the containers, run the following command:

```bash
docker-compose up
```

You can now visit and use Cyber Justitia using the following address (if you're running locally):

```url
127.0.0.1:8000
```
