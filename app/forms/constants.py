"""This module contains constants related to forms."""


from datetime import datetime, timedelta
from app.forms.utils import time_intervals


TIME_FORMAT = "%I:%M %p"


STATES = [
    (1, "Alabama"),
    (2, "Alaska"),
    (3, "Arizona"),
    (4, "Arkansas"),
    (5, "California"),
    (6, "Colorado"),
    (7, "Connecticut"),
    (8, "District of Columbia"),
    (9, "Delaware"),
    (10, "Florida"),
    (11, "Georgia"),
    (12, "Hawaii"),
    (13, "Idaho"),
    (14, "Illinois"),
    (15, "Indiana"),
    (16, "Iowa"),
    (17, "Kansas"),
    (18, "Kentucky"),
    (19, "Louisiana"),
    (20, "Maine"),
    (21, "Maryland"),
    (22, "Massaachusetts"),
    (23, "Michigan"),
    (24, "Minnesota"),
    (25, "Mississippi"),
    (26, "Missouri"),
    (27, "Montana"),
    (28, "Nebraska"),
    (29, "Nevada"),
    (30, "New Hampshire"),
    (31, "New Jersey"),
    (32, "New Mexico"),
    (33, "New York"),
    (34, "North Carolina"),
    (35, "North Dakota"),
    (36, "Ohio"),
    (37, "Oklahoma"),
    (38, "Oregon"),
    (39, "Pennsylvania"),
    (40, "Rhode Island"),
    (41, "South Carolina"),
    (42, "South Dakota"),
    (43, "Tennessee"),
    (44, "Texas"),
    (45, "Utah"),
    (46, "Vermont"),
    (47, "Virginia"),
    (48, "Washington"),
    (49, "West Virginia"),
    (50, "Wisconsin"),
    (51, "Wyoming"),
]


PACKAGE_TYPES = [(1, "Cash"), (3, "In-Kind")]


PEOPLE_RANGES = [
    (1, "Choose range..."),
    (2, "1 - 50"),
    (3, "51 - 100"),
    (4, "101 - 250"),
    (5, "251 - 500"),
    (6, "501 - 1000"),
    (7, "1001 - 2500"),
    (8, "2501 - 5000"),
    (9, "5001 - 10000"),
    (10, "10000+"),
]


# a list of a 30 minute time intervals as strings
TIMES = time_intervals(
    datetime(2019, 11, 19, 0), datetime(2019, 11, 19, 23, 30), timedelta(minutes=30), TIME_FORMAT
)
