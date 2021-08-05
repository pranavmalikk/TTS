import os
import glob
import tempfile
from typing import final
import numpy as np
from pathlib import Path
import shutil
import fnmatch
import re

label_file = 'MEGAsync Imports/Master file/Sliced Dialogue/Label files'
label_eqg_file = 'MEGAsync Imports/Master file/Sliced Dialogue/Label files/eqg'
label_fim_file = 'MEGAsync Imports/Master file/Sliced Dialogue/Label files/fim'
EQG_files = 'MEGAsync Imports/Master file/Sliced Dialogue/EQG'
FIM_files = 'MEGAsync Imports/Master file/Sliced Dialogue/FiM'
Special_files = 'MEGAsync Imports/Master file/Sliced Dialogue/Special source'


#Have to be in the right relative location to run this method have to figure work around later
class Directories:
    def __init__(self, path):
        self.path = path

    def absolute_directory(self):
        abs_path = os.path.abspath(self.path)
        return abs_path
    
    def get_directory(self):
        file_path = os.path.normpath(self.path)
        
        #file_path = absolute_directory(file_path)

        if not os.path.exists(file_path):
            print("Path of the file is Invalid. Make sure you are one step above Desktop directory.")

        else:
            file_path = self.absolute_directory()

            return file_path

    def get_name(self):
        path = os.path.normpath(self.path)
        return os.path.basename(path)


#Walks through the files and stores the file paths to an array
def walkThroughFiles(directory):
    all_files = []
    for(dirpath, dirnames, filenames) in os.walk(directory):
        for file in filenames:
            if (file.startswith("eqg") or file.startswith('fim')) and file.endswith('.txt'):
                filepath = os.path.join(dirpath, file)
                all_files.append(filepath)
    return all_files

def absolute_directory(path):
    abs_path = os.path.abspath(path)
    return abs_path


#parses and converts the text to a different output file (don't think this is necessary either)
def convert_text(path_array):
    #folder = os.path.basename(os.path.dirname(path_array)) #gets the last part of the file path (folder)
    directory = os.path.dirname(os.path.abspath(path_array[0])) #gets the directory without the exact file 
    #dir_path = os.path.dirname(os.path.realpath(path_array))
    filenames_arr = [os.path.basename(names) for names in path_array]
    first_word = [part.split("_")[0] for part in filenames_arr]

    list_of_unique_words = (list(set(first_word)))

    for words in range(len(list_of_unique_words)):
        if not os.path.exists(os.path.join(directory, list_of_unique_words[words])):
            os.makedirs(os.path.join(directory, list_of_unique_words[words]))


    for path in path_array:
        with open(path, "r") as input:
            basenames = os.path.basename(path)
            if(basenames.split("_")[0]) in list_of_unique_words:
                base_path = os.path.join(directory, (basenames.split("_")[0]))
                file_locations = os.path.join(base_path, basenames)
                with open(file_locations, 'w') as output:
                    for line in input:
                        last_word_list = line.split("\t")
                        last_word_list = last_word_list[2:]
                        for word in last_word_list:
                            output.write(word)

def rename_files(path): 
    #this will list current directory content
    for dirpath, dirnames, filenames in os.walk(path):
        newfilename = dirpath.replace("_", " ")
        os.rename(dirpath, newfilename)

#parses the speakers in each folder to a specific name so from EQG -> Pinkie, Applejack etc
def create_speaker_folder(path):
    overall_files = []
    #searches for flac files and appends them in overall files array. Do all iterations including _flac !flac .flac and flac
    for file_path in glob.glob(path + "/**/*flac", recursive = True):
        overall_files.append(file_path)
    for files in overall_files:
        character = files.split("_")[3]
        basename = os.path.basename(files)
        if not os.path.exists(os.path.join(path, character)):
            os.makedirs(os.path.join(path, character))
        else:
            if not os.path.exists(os.path.join(path, character, basename)):
                # print(os.path.join(os.path.join(path, character)))
                shutil.move(files, os.path.join(path, character))

def uniq(lst):
    last = object()
    for item in lst:
        if item == last:
            continue
        yield item
        last = item


#Creates the transcript from the Labeled files folder (does not work properly so scrapped this method)
def create_transcript(path):
    final_path = path + '/fim'
    text_files = []
    transcript_path = []
    for file_path in glob.glob(final_path + "/**/*.txt", recursive = True):
        text_files.append(file_path)
    for file in text_files:
        if 'fim' in final_path:
            if not file.endswith(('unmix.txt', 'original.txt', 'izo.txt')):
                with open(file, "r") as input:
                    for line in input:
                        character = line.split("_")[3]
                        if not os.path.exists(os.path.join(path, character)):
                            os.makedirs(os.path.join(path, character))
                        transcript = line.split("_")[6]
                        transcript_line = character + '/' + line.strip('\n') + "flac|" + transcript
                        transcript_path.append(transcript_line)
        else:
            with open(file, "r") as input:
                for line in input:
                        character = line.split("_")[3]
                        if not os.path.exists(os.path.join(path, character)):
                            os.makedirs(os.path.join(path, character))
                        transcript = line.split("_")[6]
                        transcript_line = character + '/' + line.strip('\n') + "flac|" + transcript
                        transcript_path.append(transcript_line)
    
    remove_duplicates = list(uniq(sorted(transcript_path)))

    for lines in range(len(remove_duplicates)):
        character = remove_duplicates[lines].split("/")[0]
        character_location = os.path.join(path, character, "{}.txt".format(character))
        if not os.path.exists(character_location):
            with open(character_location, "w") as output:
                output.write(remove_duplicates[lines])
        else:
            if remove_duplicates[lines] not in character_location:
                with open(character_location, "a") as append:
                    append.write(remove_duplicates[lines])

#Compiles the speakers from the EQG folder -> Outside EQG folder into respective characters
def compile_speakers(file_path):
    original_file_path = 'MEGAsync Imports/Master file/Sliced Dialogue'
    for(dirpath, dirnames, filenames) in os.walk(file_path):
        for files in dirnames:
            if 'EQG' not in files:
                if not os.path.exists(os.path.join(original_file_path, files)):
                    shutil.copytree(os.path.join(file_path, files), os.path.join(original_file_path, files))

#Creates the text files per character
def create_text_file(path):
    overall_files = []
    split_character = []
    for file_path in glob.iglob(path + "/**/*txt", recursive = True):
        overall_files.append(file_path)
    for files in overall_files:
        text_file_name = os.path.basename(files)
        transcript_line = os.path.basename(files)
        #Scrapes out the text part and manipulates it so that it's propper formatting
        if text_file_name.endswith('txt'):
            text_file_name = text_file_name.replace('txt', 'wav')
        if transcript_line.endswith('_.txt'):
            transcript_line = transcript_line.replace('_.txt','?')
        elif transcript_line.endswith('!.txt'):
            transcript_line = transcript_line.replace('!.txt', '!')
        elif transcript_line.endswith('.txt'):
            transcript_line = transcript_line.replace('.txt', '.')
        if not transcript_line.endswith(('!', '.')):
            transcript_line += "."
        split_character = text_file_name.split("_")[3:4]
        print(split_character)
        if len(split_character) > 0:
            for character in split_character:
                character_location = os.path.join(path, character, "{}.txt".format(character))
                if not os.path.exists(os.path.join(path, character)):
                    os.makedirs(os.path.join(path, character))
                if not os.path.exists(character_location):
                    with open(character_location, "w") as output:
                        output.write(character + '/' + text_file_name + '|' + transcript_line + '\n')
                else:
                    if text_file_name not in character_location:
                        #print(text_file_name)
                        with open(character_location, "a") as append:
                            append.write(character + '/' + text_file_name + '|' + transcript_line + '\n')

#removes the text file from the character folders so removes Pinkie/Pinkie.txt
#Mean Twilight Sparkle does not exist (have to delete form special sources manually)
def remove_text_files(path):
    for file_path in glob.iglob(path + "/**/*txt", recursive = True):
        stem_path = (Path(file_path).stem)
        if len(stem_path) <= 21:
            os.remove(file_path)
        # if os.path.basename(os.path.dirname(file_path)) == stem_path:
        #     os.remove(file_path)

#Checks the missing files by comparing the folder to the text file inside folder so:
#Pinkie/1.flac
#Pinkie/2.flac
#Pinkie/3.flac
#If Pinkie/3.flac does not exist in Pinkie/Pinkie.txt for some reason then it shows that
def check_missing_file(path):
    flac_array = []
    missing_files = []
    store_path = []
    store_text = []
    basenames = []
    for dirpath, dirnames, filenames in os.walk(path):
        for flac_files in filenames:
            if flac_files.endswith('.txt'):
                if(len(flac_files.split("_")) < 2):
                    store_text.append(os.path.join(dirpath, flac_files))
            elif flac_files.endswith('flac'):
                if flac_files.endswith('...flac'):
                    flac_files = flac_files.replace('...flac', "")
                elif flac_files.endswith('..flac'):
                    flac_files = flac_files.replace('..flac', "")
                elif flac_files.endswith('_.flac'):
                    flac_files = flac_files.replace('_.flac', "")
                elif flac_files.endswith('.flac'):
                    flac_files = flac_files.replace('.flac', "")
                elif flac_files.endswith('!.flac'):
                    flac_files = flac_files.replace('!.flac', "") 
                if flac_files.endswith(('!', '.')):
                    flac_files = flac_files[:-1]
                flac_array.append(flac_files)
                store_path.append(os.path.join(dirpath, flac_files))
    for text in store_text:
        with open(text, "r") as input:
            for line in input:
                if line[0:-2] not in flac_array:
                    missing_files.append(line)
    for files in missing_files:
        print(files)
    return missing_files

#Have to first run this method with the text files there regardless if they are correct or not 
#After you run this the text files should be deleted that are duplicates
#Then run this by adding in the missing files_parameter
#Then create_text_files again
#Then check missing files again
#Manually remove the ones that are not removed 
def delete_duplicates(path, missing_files):
    stripped_text = []
    missing_file_array = []
    for file in missing_files:
        stripped_text.append(file.strip("\n"))
    #print(stripped_text)
    for file_path in glob.iglob(path + "/**/*txt", recursive = True):
        for files in stripped_text:
            if files in file_path:
                os.remove(file_path)
            

        
#directory_object = Directories(label_file)
#print(directory_object.get_directory())


#first_file = walkThroughFiles(label_file)
#convert_text(first_file)

#rename_files(Special_files)

#create_speaker_folder(EQG_files)

#compile_speakers(EQG_files)

#remove_text_files('MEGAsync Imports/Master file/Sliced Dialogue/FiM')

#create_text_file(Special_files)

#missing_file = check_missing_file('MEGAsync Imports/Master file/Sliced Dialogue/FiM/') 

#delete_duplicates(path = 'MEGAsync Imports/Master file/Sliced Dialogue/FiM/', missing_files = missing_file)


#plan for tomorrow:
#1) put all the EQG/Special Source/FiM into one path outside of their respective folders
#2) compare each line by line to see which line exists in the folder and which doesn't
#3) Search up the mega to see if these exist in the file
#4) If they do exist then good, if not then convert text or the create folders method is wrong

#plan:
#Take all the text files and organize them in a transcription manner similar to before but compile the 







    















