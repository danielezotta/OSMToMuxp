import PySimpleGUI as sg
import xml.etree.ElementTree as ET

def convert(path):

    # try:
        f = open(path, "r")
        f.close()

        root = ET.parse(path).getroot()

        # get all ways, are paths
        for way in root.iter('way'):
            print("cut_polygon." + way.attrib["id"])
            altitudeTags = way.findall('tag')
            if len(altitudeTags) == 1:
                print("\televation: " + altitudeTags[0].attrib["v"])
                print("\tcoordinates:")
                for nd in way.iter('nd'):
                    node = root.find('./node[@id=\'' + nd.attrib["ref"] + '\']')
                    print("\t\t", node.attrib["lat"], ",", node.attrib["lon"])
            # else:
            #     print(way.attrib["altitude_high"], way.attrib["altitude_low"])

    # except:
    #     print("File not found")


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
        # End program if user closes window or
        # presses the OK button
        if event == "Convert":
            print(values['osm-file'])
            if values['osm-file']:
                convert(values['osm-file'])
        elif event == sg.WIN_CLOSED:
            break

    window.close()

if __name__ == '__main__':
    main()