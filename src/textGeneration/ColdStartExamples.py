COLD_START_COMPARISON_LT = """Compare (<) entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Mary</cell><cell>35</cell></row>
<row><cell>Paul</cell><cell>45</cell></row>
example: Mary is younger than Paul.
"""

COLD_START_COMPARISON_GT = """Compare (>) entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Paul</cell><cell>45</cell></row>
<row><cell>Mary</cell><cell>35</cell></row>
example: Paul is older than Mary.
"""

COLD_START_COMPARISON_EQ = """Compare (=) entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Paul</cell><cell>35</cell></row>
<row><cell>Mary</cell><cell>35</cell></row>
example: Paul has the same year as Mary.
"""

COLD_START_LOOKUP= """Read entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Mary</cell><cell>35</cell></row>
<row><cell>Paul</cell><cell>45</cell></row>
example: Mary is 35 and Paul is 45 years old.
"""


COLD_START_MIN= """Find min entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Mary</cell><cell>35</cell></row>
example: Mary is the youngest at 35 years old.
"""

COLD_START_MAX= """Find max entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Mary</cell><cell>35</cell></row>
example: Mary is the oldest at 35 years old.
"""

COLD_START_COUNT= """Count entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Mary</cell><cell>35</cell></row>
<row><cell>Paul</cell><cell>45</cell></row>
example: There are two persons.
"""

COLD_START_GROUPING_COUNT = """Count entities:

<table>Persons</table>
<count> 3 </count>
<extra>Italy<header>Country</header></extra>
<header>Name</header>
<row><cell>Mary</cell></row>
<row><cell>Paul</cell></row>
<row><cell>Mike</cell></row>
example: There are three Italian persons.
"""

COLD_START_GROUPING_COUNT_COMPARISONS = """Grouping entities:

<table>Persons</table>
<count> 3 </count>
<extra> > 12 <header>Age</header></extra>
<header>Name</header><header>Age</header>
<row><cell>Mary</cell><cell>36</cell></row>
<row><cell>Paul</cell><cell>46</cell></row>
<row><cell>Mike</cell><cell>18</cell></row>
example: There are three persons with age greater than 12.
"""