#!/usr/bin/python3

import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser(description='Convert gpx Osmand file to google kml file with mapped icons')
parser.add_argument('input_file')

args = parser.parse_args()
plik = args.input_file

icon_id = {
    # osmand_icon   : giconID, gName
    "special_arrow_right_arrow_left":[1501,"shape_diamond"],
    "special_star"                  :[1502,"shape_star"],
    "shop_pet"                      :[1507,"animal-paw"],
    "amenity_atm"                   :[1510,"atm"],
    "beach"                         :[1521,"beach"],
    "bridge_structure_arch"         :[1528,"bridge"],
    "shop_car_repair"               :[1539,"car-repair"],
    "place_city"                    :[1546,"city-buildings"],
    "building"                      :[1546,"city-buildings"],
    "restaurants"                   :[1577,"food-fork-knife"],
    "special_symbol_question_mark"  :[1594,"help"],
    "special_trekking"              :[1596,"hiking-solo"],
    "historic_castle"               :[1598,"historic-building"],
    "historic_archaeological_site"  :[1598,"historic-building"],
    "historic_ruins"                :[1598,"historic-building"],
    "tourism_hotel"                 :[1602,"hotel-bed"],
    "tourism_information"           :[1608,"info"],
    "tourism_museum"                :[1636,"museum"],
    "parking"                       :[1644,"parking"],
    "amenity_pparking"              :[1644,"parking"],
    "religion_christian"            :[1670,"religious-christian"],
    "religion_muslim"               :[1673,"religious-islamic"],
    "religion_jewish"               :[1675,"religious-jewish"],
    "shop_supermarket"              :[1685,"shopping-cart"],
    "amenity_drinking_water"        :[1703,"tap-flowing"],
    "tourism_viewpoint"             :[1729,"vista"],
    "tourism_camp_site"             :[1765,"camping_tent"],
    "natural_cave_entrance"         :[1767,"cave"],
    "nature_reserve"                :[1886,"tree-deciduous"],
    "waterfall"                     :[1892,"waterfall"],
    "special_symbol_remove"         :[1898,"x-cross"],
    "special_symbol_minus"          :[1898,"x-cross"],
    "special_marker"                :[1899,"blank-shape_pin"]
    }

icon_matrix = dict()
# 1501-d00d0d: [0,0]
# gIcon-oColor: [Desc, NoDesc]

baloon = '''
      <BalloonStyle>
        <text><![CDATA[<h3>$[name]</h3>]]></text>
      </BalloonStyle>'''

NoDesc = '-nodesc'

mapping_table = str.maketrans ({'&': "&amp;",
                                '"': "&quot;",
                                "'": "&apos;",
                                '>': "&gt;",
                                '<': "&lt;"
                                })

def iconTemplate(gIcon,gColor,gNdesc,gBaloon):
    print(f'''    <Style id="icon-{gIcon}-{gColor}{gNdesc}-normal">
      <IconStyle>
        <color>ff00eaff</color>
        <scale>1</scale>
        <Icon>
          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle> {gBaloon}
    </Style>
    <Style id="icon-{gIcon}-{gColor}{gNdesc}-highlight">
      <IconStyle>
        <color>ff00eaff</color>
        <scale>1</scale>
        <Icon>
          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <scale>1</scale>
      </LabelStyle> {gBaloon}
    </Style>
    <StyleMap id="icon-{gIcon}-{gColor}{gNdesc}">
      <Pair>
        <key>normal</key>
        <styleUrl>#icon-{gIcon}-{gColor}{gNdesc}-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#icon-{gIcon}-{gColor}{gNdesc}-highlight</styleUrl>
      </Pair>
    </StyleMap>''',file=wyjscie)

my_namespaces = dict([node for _, node in ET.iterparse(plik, events=['start-ns'])])

tree = ET.parse(plik)
root = tree.getroot()

# rootStr = root.tag[:len(root.tag)-3]
rootNS = '{'+my_namespaces['']+'}'
osmandNS = '{'+my_namespaces['osmand']+'}'
wpt = rootNS+'wpt'
wptName = rootNS+'name'
wptDesc = rootNS+'desc'
extentions = rootNS+'extensions'
oColor = osmandNS+'color'
oIcon = osmandNS+'icon'
rColor = rootNS+'color'
rIcon = rootNS+'icon'

wyjscie = open(plik[:len(plik)-4]+'.kml','w')

print('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>'''+plik[:len(plik)-4]+'''</name>''',file=wyjscie)

for wpoint in root.findall(wpt):
    print('    <Placemark>',file=wyjscie)
    print('       <name>'+ wpoint.find(wptName).text.translate(mapping_table) +'</name>',file=wyjscie)

    D = wpoint.find(wptDesc)
    C = wpoint.find(extentions).find(oColor)
    I = wpoint.find(extentions).find(oIcon)
    C = C if C is not None else wpoint.find(extentions).find(rColor)
    Ctxt = C.text[len(C.text)-6:len(C.text)]
    I = I if I is not None else wpoint.find(extentions).find(rIcon)
    if I.text in icon_id:
      Inr = icon_id[I.text][0]
    else:
      Inr = 1898
      print('advice - please, add maping in icon_id matrix for icon -> ' + I.text)
      # Ctxt = '000000'

    IC = str(Inr)+'-'+Ctxt
    if D is not None:
        print('       <description>'+ D.text +'</description>',file=wyjscie)
        gNdesc = ''
        if IC in icon_matrix: icon_matrix[IC][0] = 1
        else: icon_matrix[IC] = [1,0]
    else:
        gNdesc = NoDesc
        if IC in icon_matrix: icon_matrix[IC][1] = 1
        else: icon_matrix[IC] = [0,1]

    print(f'''       <styleUrl>#icon-{Inr}-{Ctxt}{gNdesc}</styleUrl>
        <Point>
        <coordinates>
            {wpoint.get('lon')},{wpoint.get('lat')},0
        </coordinates>
      </Point>
    </Placemark>''',file=wyjscie)

for key in icon_matrix:
    # print(key, icon_style[key], icon_style[key][0], icon_style[key][1])
    gIcon = key[0:4]
    gColor = key[5:11]
    # print(gIcon,gColor,key)
    if icon_matrix[key][0] == 1:
        gBaloon = ''
        gNdesc = ''
        iconTemplate(gIcon,gColor,gNdesc,gBaloon)
    if icon_matrix[key][1] == 1:
        gBaloon = baloon
        gNdesc = NoDesc
        iconTemplate(gIcon,gColor,gNdesc,gBaloon)

print('''  </Document>
</kml>
''',file=wyjscie)
