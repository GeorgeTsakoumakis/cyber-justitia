# CSC2033_Team25_23-24

## Cyber Justitia
[![Super-Linter](https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24/actions/workflows/linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)
[![Tests](https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24/actions/workflows/test.yml/badge.svg)](https://github.com/newcastleuniversity-computing/CSC2033_Team25_23-24/blob/george/.github/workflows/test.yml)

### Team Members:
- [Yanhao Bao](https://github.com/YanhaoBao)
- [Ziad El Krekshi](https://github.com/neuziad)
- [Ionut-Valeriu Facaeru](https://github.com/IanFacaeru)
- [Jonathan Muse](https://github.com/Musey21)
- [Ayesha Suleman](https://github.com/xayeshasulx)
- [Georgios Tsakoumakis](https://github.com/gtsakoumakis2004)

Names are listed in alphabetical order by last name.

### Project Description:
Fill later

### Installation Instructions:
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
6. Create a `.env` file in the root directory of the project and add the following environment variables:
```bash
SECRET_KEY=your_secret_key
DEBUG=False
DB_NAME=postgresql_db_name
DB_USER = postgresql_user
DB_PASSWORD = postgresql_password
DB_HOST=postgresql_host
DB_PORT='5432'
```
7. Run the following command to create a migration:
```bash
python manage.py makemigrations
```

### Running the Application:
To run the application, execute the following command:
```bash
python manage.py runserver
```
If static assets are not being served, run the following command:
```bash
python manage.py collectstatic
```


### Testing Instructions:
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
