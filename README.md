<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GNU License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<h3 align="center">Football Manager Scouting</h3>

  <p align="center">
    A tool for facilitating data-driven scouting in Football Manager
    <br />
    <a href="https://github.com/HannesLindback/Football-Manager-scouting"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/HannesLindback/Football-Manager-scouting/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/HannesLindback/Football-Manager-scouting/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Football Manager Scouting is a python program for making data driven scouting easier in the FM games.

It currently provides two scouting tools:

  · ```Spider```: Creates a radar chart (or, "spider") comparing the statistics of a player from your session with either the statistics of another player or with the average stats of a group of players.
  
  · ```Index```: Creates a csv file displaying categorical information of the player  (contract info, club, division, attributes etc.) and most importantly, a score for each statistical category as well as an overall index, showing how good the players has performed compared to the other players in dataset.

The program works by taking the raw rtf-file printed from the game, processing each value for each player, and saving them to an SQL database. When either of the two tools, Spider or Index, are used, the program retrieves the relevant data from the database and generates the desired radar chart or csv-file. The ```insert_data``` module is therefore the entire programs entry point as it saves the player data to the database.

Football Manager Scouting also makes it possible to compare players/clubs/divisoin over several seasons by adding players to the database after every in-game season. Football Manager otherwise deletes a lot of data after a new season has started, making it difficult to, for instance, compare changes in age structure of your squad over the seasons.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started
1) The first step is to download the data from Football Manager:
  1a) In the scouting of the game, use the provided view from moneyball.fmf,
  1b) Select all players, print, and save as text file (to rtf format).
2) Create an empty PostgreSQL database,
3) Install package: ```pip install football-manager-scouting```.

See <a href="#readme-top">Usage</a> for examples of how to insert data and use Spider and Index.

### Prerequisites

* PostgreSQL,
* Python >= 3.8,
* SQLAlchemy >= 2.0
* psycopg2-binary >= 2.0
* tqdm >= 4.0
* Soccerplots = 1.0

### Installation

```pip install football-manager-scouting```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Import the tools.
```
from football_manager_scouting.spider import spider
from football_manager_scouting.index import index
from football_manager_scouting.insert_data import insert_data
```

Create a dictionary with the login information to the PostgreSQL database.
```
db_login = {
  'user': 'username',
  'password': 'password',
  'host': 'localhost:5432',
  'database': 'database'
}
```

Insert the downloaded data to the database.
```
insert_to_database(
                   db_login=db_login,
                   path='./data.rtf',  # The path to the downloaded file with the player data.
                   season=24,          # The current in-game season.
                   total=50435,        # The total number of players in the data file. For the progress bar. OPTIONAL.
                   n=50000             # After how many players should entries be commited to the database. For datafile with a large number (>100000) of players it is recommended to do several smaller commits.
)              
```

Create a radar chart of a player comparing him to the other players of that position in the same division. The chart will be saved to ./spider.jpg

```
spider(
       db_login=db_login,
       name='John Doe',           # The name of the player.
       comparison='average',      # If the comparison should be to another player or to the average of multiple players.
       category='DC',             # Filter which statistical categories that should be used in chart.
       position='DC',             # The position of the players.
       mins=500,                  # The minimum number of minutes a player should have played to be included.
       division='Premier League'  # The division of the players.
)
```

Create an index csv file. The file will be saved to a csv file named after the category in the working directory.
```
index(
      db_login=db_login,
      category='STC',       # Filter which statistical categories that should be used in the index.
      position='STC, AMC',  # The position of the players.
      mins=500,             # The minimum number of minutes a player should have played to be included.
      division=None         # The division of the included players. None means that it will not filter on division.
)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the GNU License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Hannes Lindbäck - hanneskarllindback@gmail.com

Project Link: [https://github.com/HannesLindback/Football-Manager-scouting](https://github.com/HannesLindback/Football-Manager-scouting)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/HannesLindback/Football-Manager-scouting.svg?style=for-the-badge
[contributors-url]: https://github.com/HannesLindback/Football-Manager-scouting/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/HannesLindback/Football-Manager-scouting.svg?style=for-the-badge
[forks-url]: https://github.com/HannesLindback/Football-Manager-scouting/network/members
[stars-shield]: https://img.shields.io/github/stars/HannesLindback/Football-Manager-scouting.svg?style=for-the-badge
[stars-url]: https://github.com/HannesLindback/Football-Manager-scouting/stargazers
[issues-shield]: https://img.shields.io/github/issues/HannesLindback/Football-Manager-scouting.svg?style=for-the-badge
[issues-url]: https://github.com/HannesLindback/Football-Manager-scouting/issues
[license-shield]: https://img.shields.io/github/license/HannesLindback/Football-Manager-scouting.svg?style=for-the-badge
[license-url]: https://github.com/HannesLindback/Football-Manager-scouting/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/hannes-lindback
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://python.org/
[SQLAlchemy.org]: https://img.shields.io/badge/SQLAlchemy-306998?logo=python&logoColor=white
[SQLAlchemy-url]: https://sqlalchemy.org/