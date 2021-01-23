import PySimpleGUI as sg
import xml.etree.ElementTree as ET


def getTileDef(lat, lon):
    print(lat)
    lat = int(lat)
    lon = int(lon)
    formattedTileString = '%+d%+04d' % (lat, lon)
    print(formattedTileString)
    return formattedTileString


def getArea(path, lat, lon):
    root = ET.parse(path).getroot()
    arrlat, arrlon = [], []
    for node in root.findall('node'):
        templat = int(node.attrib["lat"].split(".")[0])
        templon = int(node.attrib["lon"].split(".")[0])
        if templat == int(lat) and templon == int(lon):
            arrlat.append(float(node.attrib["lat"]))
            arrlon.append(float(node.attrib["lon"]))
    minlat = max(min(arrlat) - 0.001, float(lat))
    maxlat = min(max(arrlat) + 0.001, float(lat) + 1)
    minlon = max(min(arrlon) - 0.001, float(lon))
    maxlon = min(max(arrlon) + 0.001, float(lon) + 1)
    formattedTileString = '%f %f %f %f' % (minlat, maxlat, minlon, maxlon)
    print(formattedTileString)
    return formattedTileString


def convert(path, lat, lon):
    # output for file
    output = ""

    # get root of document
    root = ET.parse(path).getroot()

    # get all ways, are paths
    for way in root.iter('way'):
        # Check if point is out of selected coords
        coords = root.find('./node[@id=\'' + way.find('nd').attrib["ref"] + '\']')
        if (coords.attrib["lat"].split(".")[0] == lat and coords.attrib["lon"].split(".")[0] == lon):

            # get altitude tags
            altitudeTags = way.findall('tag')
            # Check if only one tag set, so flatten
            if len(altitudeTags) == 1:
                output += ("cut_polygon." + way.attrib["id"] + ":\n")
                output += ("\televation: " + altitudeTags[0].attrib["v"] + "\n")
                output += ("\tcoordinates:" + "\n")
                for nd in way.iter('nd'):
                    node = root.find('./node[@id=\'' + nd.attrib["ref"] + '\']')
                    output += ("\t\t - " + node.attrib["lat"] + "\t" + node.attrib["lon"] + "\n")

                output += "\n"

            # More tags, so its gradient
            else:
                output += ("cut_ramp." + way.attrib["id"] + ":" + "\n")
                output += ("\tcoordinates:" + "\n")
                for nd in way.iter('nd'):
                    node = root.find('./node[@id=\'' + nd.attrib["ref"] + '\']')
                    output += ("\t\t - " + node.attrib["lat"] + "\t" + node.attrib["lon"] + "\n")
                output += ("\t3d_coordinates:" + "\n")

                # find first node for height
                node_1 = root.find('./node[@id=\'' + way.findall('nd')[0].attrib["ref"] + '\']')
                node_2 = root.find('./node[@id=\'' + way.findall('nd')[1].attrib["ref"] + '\']')
                node_3 = root.find('./node[@id=\'' + way.findall('nd')[2].attrib["ref"] + '\']')
                node_4 = root.find('./node[@id=\'' + way.findall('nd')[3].attrib["ref"] + '\']')

                latTop = (float(node_1.attrib["lat"]) + float(node_4.attrib["lat"])) / 2
                lonTop = (float(node_1.attrib["lon"]) + float(node_4.attrib["lon"])) / 2
                latBot = (float(node_2.attrib["lat"]) + float(node_3.attrib["lat"])) / 2
                lonBot = (float(node_2.attrib["lon"]) + float(node_3.attrib["lon"])) / 2
                latDist = (latTop - latBot) / 8
                lonDist = (lonTop - lonBot) / 8

                output += ("\t\t - " + str(latTop - latDist) + "\t" + str(lonTop - lonDist) + "\t" + way.find('tag[@k="altitude_high"]').attrib["v"] + "\n")
                output += ("\t\t - " + str(latBot + latDist) + "\t" + str(lonBot + lonDist) + "\t" + way.find('tag[@k="altitude_low"]').attrib["v"] + "\n")

                output += "\n"

    return output


def main():
    layout = [
        [sg.FileBrowse("OSM file", file_types=((".osm", "*.osm"),)), sg.In("Select OSM file to convert", key='osm-file')],
        [sg.Text("Output file name", size=(15, 1)), sg.In("", key='output-name')],
        [sg.Text("Id", size=(15, 1)), sg.In("", key='output-id')],
        [sg.Text("Version", size=(15, 1)), sg.In("", key='output-version')],
        [sg.Text("Description", size=(15, 1)), sg.In("", key='output-description')],
        [sg.Text("Author", size=(15, 1)), sg.In("", key='output-author')],
        [sg.Text("Elevation step", size=(15, 1)), sg.In("", key='output-step')],
        [sg.Text("Source dsf", size=(15, 1)), sg.In("", key='output-dsf')],
        [sg.Button("Convert", size=(15, 1), pad=(150, 2))],
        [sg.Text("Waiting", key='state', justification='center', size=(100, 1))]
              ]

    # Create the window
    window = sg.Window("OSMToMuxp", layout, size=(400, 280), margins=(0, 5))

    # Create an event loop
    while True:
        event, values = window.read()

        if event == "Convert":
            print(values['osm-file'])
            if values['osm-file']:
                try:
                    f = open(values['osm-file'], "r")
                    f.close()
                    coords = []
                    root = ET.parse(values['osm-file']).getroot()
                    for node in root.findall('node'):
                        nodeLat = node.attrib["lat"].split(".")[0]
                        nodeLon = node.attrib["lon"].split(".")[0]
                        if (nodeLat, nodeLon) not in coords:
                            coords.append((nodeLat, nodeLon))
                    # different files for coordinates
                    index = 1
                    for coord in coords:

                        window['state'].update('Doing file %d' % index)

                        # Erase file content if exists
                        open('%s_%d.muxp' % (values['output-name'], index), 'w').close()

                        # Write configuration to file
                        file = open('%s_%d.muxp' % (values['output-name'], index), "a")
                        file.write("muxp_version: 0.3\n")
                        file.write("id: " + values['output-id'] + "\n")
                        file.write("version: " + values['output-version'] + "\n")
                        file.write("description: " + values['output-description'] + "\n")
                        file.write("author: " + values['output-author'] + "\n")
                        file.write("tile: " + getTileDef(coord[0], coord[1]) + "\n")
                        file.write("source_dsf: " + values['output-dsf'] + "\n")
                        file.write("elevation_step: " + values['output-step'] + "\n")
                        file.write("area: " + getArea(values['osm-file'], coord[0], coord[1]) + "\n\n")

                        # Different files
                        file.write(convert(values['osm-file'], coord[0], coord[1]))
                        file.close()
                        index += 1

                    window['state'].update('Finished')

                except:
                    print("File not found")

        elif event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == '__main__':
    main()