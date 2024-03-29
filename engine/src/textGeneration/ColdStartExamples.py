COLD_START_COMPARISON_LT = """Compare (<) entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Enzo</cell><cell>35</cell></row>
<row><cell>Paolo</cell><cell>45</cell></row>
example: Enzo is younger than Paolo.
"""

COLD_START_COMPARISON_GT = """Compare (>) entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Paolo</cell><cell>45</cell></row>
<row><cell>Enzo</cell><cell>35</cell></row>
example: Paolo is older than Enzo.
"""

COLD_START_COMPARISON_EQ = """Compare (=) entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Paolo</cell><cell>35</cell></row>
<row><cell>Enzo</cell><cell>35</cell></row>
example: Paolo has the same year as Enzo.
"""

COLD_START_LOOKUP = """Read entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Enzo</cell><cell>35</cell></row>
<row><cell>Paolo</cell><cell>45</cell></row>
example: Enzo is 35 and Paolo is 45 years old.
"""

COLD_START_MIN = """Find min entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Enzo</cell><cell>35</cell></row>
example: Enzo is the youngest at 35 years old.
"""

COLD_START_MAX = """Find max entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Enzo</cell><cell>35</cell></row>
example: Enzo is the oldest at 35 years old.
"""

COLD_START_COUNT = """Count entities:

<table>Persons</table>
<header>Name</header><header>Year</header>
<row><cell>Enzo</cell><cell>35</cell></row>
<row><cell>Paolo</cell><cell>45</cell></row>
example: There are two persons.
"""

COLD_START_GROUPING_COUNT = """Count entities:

<table>Persons</table>
<count> 3 </count>
<extra>Italy<header>Country</header></extra>
<header>Name</header>
<row><cell>Enzo</cell></row>
<row><cell>Paolo</cell></row>
<row><cell>Mike</cell></row>
example: There are three Italian persons.
"""

COLD_START_GROUPING_COUNT_COMPARISONS = """Grouping entities:

<table>Persons</table>
<count> 3 </count>
<extra> > 12 <header>Age</header></extra>
<header>Name</header><header>Age</header>
<row><cell>Enzo</cell><cell>36</cell></row>
<row><cell>Paolo</cell><cell>46</cell></row>
<row><cell>Mike</cell><cell>18</cell></row>
example: There are three persons with age greater than 12.
"""
