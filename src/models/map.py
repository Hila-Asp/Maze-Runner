ROW_LENGTH = 25
COLUMN_LENGTH = 25
BLOCK_PIXEL_WIDTH = 27
BLOCK_PIXEL_HEIGHT = 27
MAP_DOCUMENT_FILE_PATH = "C:/Networks/Final_Project/map/Maps.txt"


class Map:
    def __init__(self):
        self.doc_address = MAP_DOCUMENT_FILE_PATH  # The location to the Maps.txt
        self.map_options_list = self.__get_maps_from_doc()  # A list that each item is a string that represents a map

    def __get_maps_from_doc(self):
        """
        This function reads from Maps.txt and creates a list that each item is a line from the file
        :return: A list that each item is a string that represent a map
        """
        map_list = []  # creates a empty list that later on will contain in each index a String of the numbers that are blocks in the map
        map_txt_file = open(self.doc_address, "r")
        for map_line in map_txt_file:  # inserts to the list
            map_list.append(map_line)
        map_txt_file.close()
        return map_list

    def create_block_list(self, index):
        """
        This function creates a list of block locations from map_options_list[index]
        :param index: The index of the chosen map in the list
        :return: A list of tuples that each tuple is a location of a block
        """
        blocks = self.map_options_list[index].rstrip('\n').split('/')
        # When I split map_options_list[index] using only strip('/')-
        # The last item which is a string has the \n as part of the string
        # Therefore i use rstrip('\n').split('/')- to first remove the \n and then split the string.
        # Example for blocks = ['(0, 0)', '(0, 27)', '(0, 81)']
        for i in range(len(blocks)):
            blocks[i] = blocks[i][1:-1]  # Removes the parentheses ()
            x, y = blocks[i].split(', ')
            blocks[i] = (int(x), int(y))
        return blocks
