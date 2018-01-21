from imposm.parser import OSMParser
import csv


class AddressParser:

    def __init__(self, pbf_path, boroughs_path):
        self.pbf_path = pbf_path
        self.boroughs_path = boroughs_path
        self._nodes = {}
        self._out = None
        self._csvwriter = None
        self.boroughs = {}
        with open(boroughs_path, mode='r', encoding='utf-8') as f:
            for line in f:
                values = line.split(',')
                self.boroughs[values[0]] = values[1].strip()

    def _nodes_callback(self, nodes):
        for osm_id, tags, coords in nodes:
            if all(col in tags for col in ['addr:street', 'addr:housenumber',
                                           'addr:postcode']):
                street = tags['addr:street']
                housenumber = tags['addr:housenumber']
                postcode = tags['addr:postcode']
                city = tags.get('addr:city', 'New York')
                borough = self.boroughs.get(postcode, 'NULL')

                self._csvwriter.writerow([str(osm_id),
                                          str(coords[0]),
                                          str(coords[1]),
                                          street,
                                          housenumber,
                                          postcode,
                                          city,
                                          borough])
                self._nodes[osm_id] = None
            else:
                self._nodes[osm_id] = coords

    def _coords_callback(self, coords):
        for osm_id, lon, lat in coords:
            if osm_id not in self._nodes:
                self._nodes[osm_id] = (lon, lat)

    def _ways_callback(self, ways):
        for osm_id, tags, refs in ways:
            if all(col in tags for col in ['addr:street', 'addr:housenumber',
                                           'addr:postcode']):
                for ref in refs:
                    try:
                        node = self._nodes[ref]
                        if node is None:
                            break
                        street = tags['addr:street']
                        housenumber = tags['addr:housenumber']
                        postcode = tags['addr:postcode']
                        city = tags.get('addr:city', 'New York')
                        borough = self.boroughs.get(postcode, 'NULL')

                        self._csvwriter.writerow([str(osm_id),
                                                  str(node[0]),
                                                  str(node[1]),
                                                  street,
                                                  housenumber,
                                                  postcode,
                                                  city,
                                                  borough])
                        del self._nodes[ref]
                        break
                    except KeyError:
                        pass

    def _relations_print(self, relations):
        for rel in relations:
            print(rel)

    def _ways_print(self, ways):
        for way in ways:
            print(way)

    def _nodes_print(self, nodes):
        for node in nodes:
            print(node)

    def parse_address(self, csv_path):
        self._out = open(csv_path, 'w', encoding='utf-16')
        self._csvwriter = csv.writer(self._out, delimiter='|',
                                     doublequote=False, quoting=csv.QUOTE_NONE)
        self._csvwriter.writerow(['Id', 'Dlugosc', 'Szerokosc', 'Ulica',
                                  'Numer', 'Kod_pocztowy',
                                  'Miasto', 'Dzielnica'])
        parser = OSMParser(concurrency=4, nodes_callback=self._nodes_callback,
                           coords_callback=self._coords_callback)
                           # ways_callback=self._ways_print)
        parser.parse(self.pbf_path)

        parser = OSMParser(concurrency=4, ways_callback=self._ways_callback)
        parser.parse(self.pbf_path)

        print(len(self._nodes))
        self._nodes = {}
        self._out.close()


if __name__ == '__main__':
    parser = AddressParser('new-york-latest.osm.pbf', 'dzielnice.csv')
    parser.parse_address('adresy.csv')
