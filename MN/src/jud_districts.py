import os
import pandas

parent_folder = './'
parent_folder = os.path.abspath(parent_folder)
filename = os.path.join( parent_folder, 'MN_Judicial Districts.txt')



with open( filename, 'r') as f:
    lines = f.readlines()

district_county = []
for l in lines:
    distr_counties = l.split(',')    # expect comma separated

    # expect first entry is the district; all following entries are county names.
    district = distr_counties[0].strip()
    for c in distr_counties[1:]:
        district_county.append([distr_counties[0], c.strip()])

# End result: expect clean table with two columns; first is judicial district; 
# second is the county name.

df = pandas.DataFrame(data=district_county, columns=['JUD_DISTR', 'COUNTY_NAM'])
name2num = {
    'First District': 1,
    'Second District': 2,
    'Third District': 3,
    'Fourth District': 4,
    'Fifth District': 5,
    'Sixth District': 6,
    'Seventh District': 7,
    'Eighth District': 8,
    'Ninth District': 9,
    'Tenth District': 10
}
# Names cannot be longer that 10 char for shp files
df['JD_NO'] = [name2num[e] for e in df['JUD_DISTR']]
df['JD_COD'] = [str(i).zfill(2) for i in df['JD_NO']]

# todo - county name to numerical county code.
# though, this may be part of different code, not here.

county2jd = {c:j for j,c in df[['JD_NO', 'COUNTY_NAM']].values}