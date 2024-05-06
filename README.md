# CSC2033_Team25_23-24

## Cyber Justitia

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
