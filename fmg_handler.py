import struct
import sys

class Entry:
    def __init__(self, id = None, text = None):
        self.id = id
        self.text = text

class Group:
    def __init__(self, offsetIndex = None, firstID = None, lastID = None):
        self.offsetIndex = offsetIndex
        self.firstID = firstID
        self.lastID = lastID

class FMGHandler:
    def __init__(self, messages: list[Entry] = None):
        if messages == None:
            messages = []
        self.messages = messages
    
    @classmethod
    def load_from_file_content(cls, file_content):
        master_offset = 0
        
        (unk00, bigEndian, version, unk03, fileSize, unk08, unk09, unk0A, unk0B, 
         groupCount, stringCount, stringOffsetsOffset) = struct.unpack_from("<BBBBIBBBBIII", file_content, offset=master_offset)
        
        master_offset = 0x1C  # set offset to length of the header.
        
        string_offsets = struct.unpack_from(f"<{stringCount}I", file_content, offset=stringOffsetsOffset)

        entries = []
        for i in range(groupCount):
            (offsetIndex, firstID, lastID) = struct.unpack_from("<III", file_content, offset=master_offset)           
            master_offset += struct.calcsize("<III")
            
            for j in range(lastID - firstID + 1):
                extracted = b''
                offset = 0
                
                if string_offsets[offsetIndex] != 0:
                    curByte: bytes = file_content[string_offsets[offsetIndex] + offset : string_offsets[offsetIndex] + offset + 2]
                    while curByte[0:2] != b'\x00\x00':
                        extracted = extracted + curByte[0:2]
                        offset += 2
                        curByte: bytes = file_content[string_offsets[offsetIndex] + offset : string_offsets[offsetIndex] + offset + 2]

                    id = firstID + j
                    entries.append(Entry(id, extracted.decode('utf-16')))
                else:
                    id = firstID + j
                    entries.append(Entry(id, ""))
                offsetIndex += 1

        return entries
             
    def export_as_binary(self):
        header_offset = 0x1C
        groupCount = 0

        self.messages.sort(key = lambda message: message.id)

        groups: list[Group] = []
        curGroupNum = 0
        groupIter = iter(range(len(self.messages)))
        for i in groupIter:
            groupStartIndex = i
            firstId = self.messages[i].id
            while i < (len(self.messages) - 1) and self.messages[i+1].id == self.messages[i].id + 1:
                i += 1
                next(groupIter, None)
            
            lastId = self.messages[i].id
            groups.append(Group(groupStartIndex, firstId, lastId))
            curGroupNum += 1

        groupCount = len(groups)
        groupsOffset = groupCount * struct.calcsize("<III")

        strings_offset_offset = header_offset + groupsOffset
        packed_string_offsets = b""
        packed_strings = b""
        packed_groups = b""

        groupIndex = 0
        current_string_offset = strings_offset_offset + (len(self.messages) * struct.calcsize("@I"))
        for message in self.messages:
            if groupIndex < groupCount and message.id == groups[groupIndex].firstID:
                packed_groups += struct.pack("@III", groups[groupIndex].offsetIndex, groups[groupIndex].firstID, groups[groupIndex].lastID)
                groupIndex += 1
            if message.text != "":
                encodedMessage = message.text.encode('utf_16_le') + b"\x00\x00"

                if message.id == 9019:
                    encodedMessage = "Clod was here (but automatically)".encode('utf_16_le') + b"\x00\x00"

                packed_strings += encodedMessage
                packed_string_offsets += struct.pack("@I", current_string_offset)
                current_string_offset += len(encodedMessage)
            else:
                packed_string_offsets += struct.pack("@I", 0)

        fileLength = current_string_offset

        # unk00, bigEndian, version, unk03, fileSize, unk08, unk09, unk0A, unk0B, groupCount, stringCount, stringOffsetsOffset
        header = struct.pack("@BBBBIBBBBIIII", 0, 0, 1, 0, fileLength, 1, 0, 0, 0, groupCount, len(self.messages), strings_offset_offset, 0)
        
        return header + packed_groups + packed_string_offsets + packed_strings