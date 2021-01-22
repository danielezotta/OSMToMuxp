import PySimpleGUI as sg
import xml.etree.ElementTree as ET


def getTileDef(lat, lon):
    lat = int(lat.split('.')[0])
    lon = int(lon.split('.')[0])
    formattedTileString = '%+d%+04d' % (lat, lon)
    print(formattedTileString)
    return formattedTileString


def getArea(lat, lon):
    baseValueForLong = 0.000001
    lat = int(lat.split('.')[0])
    lon = int(lon.split('.')[0])
    formattedTileString = '%f %f %f %f' % (lat + baseValueForLong, lon + baseValueForLong, lat - baseValueForLong + 1, lon - baseValueForLong + 1)
    print(formattedTileString)
    return formattedTileString


def convert(path):
    # get root of document
    root = ET.parse(path).getroot()

    # get all ways, are paths
    for way in root.iter('way'):
        # get altitude tags
        altitudeTags = way.findall('tag')
        if len(altitudeTags) == 1:
            print("cut_polygon." + way.attrib["id"] + ":")
            print("\televation: " + altitudeTags[0].attrib["v"])
            print("\tcoordinates:")
            for nd in way.iter('nd'):
                node = root.find('./node[@id=\'' + nd.attrib["ref"] + '\']')
                print("\t\t - ", node.attrib["lat"], "\t", node.attrib["lon"])
        else:
            print("cut_ramp." + way.attrib["id"] + ":")
            print("\tcoordinates:")
            for nd in way.iter('nd'):
                node = root.find('./node[@id=\'' + nd.attrib["ref"] + '\']')
                print("\t\t - ", node.attrib["lat"], "\t", node.attrib["lon"])
            print("\t3d_coordinates:")

            # find first node for height
            node = root.find('./node[@id=\'' + way.findall('nd')[0].attrib["ref"] + '\']')
            print("\t\t - ", node.attrib["lat"], "\t", node.attrib["lon"], "\t", way.find('tag[@k="altitude_high"]').attrib["v"])

            # find second node for height
            node = root.find('./node[@id=\'' + way.findall('nd')[1].attrib["ref"] + '\']')
            print("\t\t - ", node.attrib["lat"], "\t", node.attrib["lon"], "\t", way.find('tag[@k="altitude_low"]').attrib["v"])


def main():
    layout = [
        [sg.FileBrowse("OSM file", file_types=((".osm", "*.osm"),)), sg.In("Select OSM file to convert", key='osm-file')],
        [sg.Button("Convert")]
              ]

    # Create the window
    window = sg.Window("OSMToMuxp", layout, size=(400, 200))

    # Create an event loop
    while True:
        event, values = window.read()

        if event == "Convert":
            print(values['osm-file'])
            if values['osm-file']:
                try:
                    f = open(values['osm-file'], "r")
                    f.close()
                    getArea("46.36027835267391", "11.03250700995257")
                    getTileDef("46.36027835267391", "11.03250700995257")
                    convert(values['osm-file'])
                except:
                    print("File not found")
        elif event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == '__main__':
    main()