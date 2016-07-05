'''
Created on Jul 1, 2016

@author: walter
'''
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

' The second Python project '
' Download html files from EDGAR '

__author__ = 'Walter Xiong'

import os
from urllib import urlopen
import socket
import argparse
import sys
import re
import shutil

#Catch index
def main(argv):

    global index_rows
    global conn_error
    global io_error
    global no_found
    global target_name
    global result_dir

    # Catch user requirement in command line
    parser=argparse.ArgumentParser()

    parser.add_argument('--target',nargs='*')

    args=parser.parse_args()

    if args.target == None:
        print ' ****************** Warning ****************** '
        print "Details: '--target' is missing"
        print "Suggestion: --targrt 10-Q 10-K"
        print ' ********************************************* '
        sys.exit()
    else:
        target=args.target

    count=0

    #Automatically detect .idx file in current directory
    for dirpath,dirnames,filenames in os.walk(os.path.abspath('.')):
        for filename in filenames:
            if os.path.splitext(filename)[1]=='.idx':
                index_file=open(os.path.join(dirpath,filename))
                index_rows=index_file.readlines()
                index_file.close()
                result_dir=os.path.join(dirpath,os.path.splitext(filename)[0])
                count+=1

    #Create related directories
    if count==0:
        print" Error: No index file found "
        sys.exit()
    elif count>1:
        print" Error: Multiple index files found "
        sys.exit()
    else:
        if os.path.isdir(result_dir):
            shutil.rmtree(result_dir)

        if not os.path.isdir(result_dir):
            os.mkdir(result_dir)

        for t in target:
            if t=='10-K' or t=='10-Q':
                target_dir=os.path.join(result_dir,t)
                if not os.path.isdir(target_dir):
                    os.mkdir(target_dir)
            elif t=='8-K':
                target_dir=os.path.join(result_dir,t)
                if not os.path.isdir(target_dir):
                    os.mkdir(target_dir)
                    os.mkdir(os.path.join(target_dir,'Press Release'))
            elif t=='Others':
                target_dir = os.path.join(result_dir, t)
                if not os.path.isdir(target_dir):
                    os.mkdir(target_dir)
                    os.mkdir(os.path.join(target_dir,'UPLOAD'))
                    os.mkdir(os.path.join(target_dir, 'CORRESP'))
                    os.mkdir(os.path.join(target_dir, 'SC 13G'))
                    os.mkdir(os.path.join(target_dir, 'SC 13GA'))
                    os.mkdir(os.path.join(target_dir, 'DEF 14A'))
                    os.mkdir(os.path.join(target_dir, '10-K405'))
            else:
                print" Error: Target %r can not be found "%t
                sys.exit()

        conn_error=open(os.path.join(result_dir,'ConnError.txt'),'w')
        io_error=open(os.path.join(result_dir,'IOError.txt'),'w')
        no_found=open(os.path.join(result_dir,'Not_Found.txt'),'w')

        #Skip useless rows
        while not(index_rows[0].startswith("---")):
            print index_rows[0]
            index_rows.pop(0)
        print(index_rows[0])
        index_rows.pop(0)

        #Download required type
        target_name = []

        if '10-K' in target:
            target_name.append('10-K')
        if '10-Q' in target:
            target_name.append('10-Q')
        if '8-K' in target:
            target_name.append('8-K')
        if 'Others' in target:
            target_name.append('UPLOAD')
            target_name.append('CORRESP')
            target_name.append('SC 13G')
            target_name.append('SC 13G/A')
            target_name.append('DEF 14A')
            target_name.append('10-K405')
        download_index_file()

#For each index, download html file
def download_index_file():

    global text_name
    global split_row
    global text_line
    global text_content
    global new_row

    file_count=0

    for row in index_rows:

        file_count+=1

        new_row=re.sub('[\n\r]','',row)

        split_row=new_row.split('|')

        if split_row[2] in target_name:

            text_name=split_row[4]

            text_url='http://www.sec.gov/Archives/'+text_name

            print 'File ' + repr(file_count) +' of ' + repr(len(index_rows)) + '\n'

            try:
                text_content = urlopen(text_url)
                download_htm()

            except socket.error:
                print('Error: SocketError found')
                conn_error.write(new_row + '\n')
            except IOError:
                print('Error: IOError found')
                io_error.write(new_row + '\n')


#From FILENAME download htm and pdf
def download_htm():

    htm_file=''
    date=''
    sic=''
    file_name_found = False
    press_release_found=False

    text_line = text_content.readline()

    while not (text_line.startswith('</SEC-HEADER>')):
        if text_line.startswith("FILED AS OF DATE:"):
            date = text_line.split(':')[1].lstrip('\t').rstrip('\n')
        if "STANDARD INDUSTRIAL CLASSIFICATION:" in text_line:
            if ']' in text_line:
                sic = text_line.split('[')[1].rstrip(']\n')
            else:
                sic = text_line.split(':')[1].lstrip(' ').rstrip(']\n')
        if "    <title>SEC.gov | File Not Found Error Alert (404)</title>\n" in text_line:
            file_name_found=False
            break

        text_line = text_content.readline()

    while not (text_line.startswith('<TEXT>')):

        if text_line.startswith('<FILENAME>'):
            file_name_found = True
            if text_line.endswith('.pdf\n') or text_line.endswith('.txt\n') or text_line.endswith('.htm\n'):
                htm_file = text_line.split('>')[1].rstrip('\n')
        if text_line.startswith('<DESCRIPTION>') and 'release' in text_line.lower():
            press_release_found=True

        text_line = text_content.readline()

    if file_name_found == False:
        no_found.write(new_row + '\n')

    if htm_file!='':

        print 'Downloading .htm/.txt/.pdf file...\n'

        no_hyphen_text_name=text_name.replace('-','')

        new_url='http://www.sec.gov/Archives/'+no_hyphen_text_name.rstrip('.txt')+'/'+htm_file

        local_file_part=text_name.split('/')[2]+'--'+text_name.split('/')[3].rstrip('.txt')

        if split_row[2]=='10-K':
            local_file=os.path.join(os.path.join(result_dir,'10-K'),local_file_part+'--'+htm_file)
        elif split_row[2]=='10-Q':
            local_file = os.path.join(os.path.join(result_dir, '10-Q'), local_file_part + '--' + htm_file)
        elif split_row[2]=='8-K' and press_release_found!=True:
            local_file = os.path.join(os.path.join(result_dir, '8-K'), local_file_part + '--' + htm_file)
        elif split_row[2]=='8-K' and press_release_found==True:
            local_file = os.path.join(os.path.join(os.path.join(result_dir, '8-K'),'Press Release'), local_file_part + '--' + htm_file)
        elif split_row[2] == 'UPLOAD':
            local_file = os.path.join(os.path.join(os.path.join(result_dir, 'Others'), 'UPLOAD'),
                                      local_file_part + '--' + htm_file)
        elif split_row[2] == 'CORRESP':
            local_file = os.path.join(os.path.join(os.path.join(result_dir, 'Others'), 'CORRESP'),
                                      local_file_part + '--' + htm_file)
        elif split_row[2] == 'SC 13G':
            local_file = os.path.join(os.path.join(os.path.join(result_dir, 'Others'), 'SC 13G'),
                                      local_file_part + '--' + htm_file)
        elif split_row[2] == 'SC 13G/A':
            local_file = os.path.join(os.path.join(os.path.join(result_dir, 'Others'), 'SC 13GA'),
                                      local_file_part + '--' + htm_file)
        elif split_row[2] == 'DEF 14A':
            local_file = os.path.join(os.path.join(os.path.join(result_dir, 'Others'), 'DEF 14A'),
                                      local_file_part + '--' + htm_file)
        elif split_row[2] == '10-K405':
            local_file = os.path.join(os.path.join(os.path.join(result_dir, 'Others'), '10-K405'),
                                      local_file_part + '--' + htm_file)

        try:
            htm_content = urlopen(new_url)
            htm_lines=htm_content.read()
            htm_content.close()

            htm_download=open(local_file,'w')
            htm_download.write("COMPANY NAME: " + split_row[1] + '\n')
            htm_download.write("CIK: " + split_row[0] + '\n')
            htm_download.write("SIC: " + sic + '\n')
            htm_download.write("FILING DATE: " + date + '\n\n\n')
            htm_download.write(htm_lines)
            htm_download.close()

        except socket.error:
            print('Error: SocketError found')
            conn_error.write(new_row + '\n')
        except IOError:
            print('Error: IOError found')
            io_error.write(new_row + '\n')

if __name__ == '__main__':
    main(sys.argv[1:])
