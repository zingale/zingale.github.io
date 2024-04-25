#!/usr/bin/env python

lineNum = 0
figureIndex = 0

"""

apjify version 0.4

5-1-2007
Michael Zingale
zingale@ucolick.org


Simple attempt at taking a manuscript for ApJ and renaming all the figures
to f1.eps, f2.eps, ..., as required for electronic submission.  Nothing is
overwritten, instead, a copy is made.  Even so, it is strongly recommended
that you make a backup of the manuscript before running this.  Everyone does
things a little differently, and it is hard to foresee all problems.  Should
anything happen to your future Noble Prize winning manuscript, I am not
responsible.

This is rather hastily written, and certainly not as elegant as it should
be.  I've tried to make it somewhat robust though.

There are two tricky cases:

\begin{figure}
\plotone{plota.eps}
\plotone{plotb.eps}
\plotone{plotc.eps}
\end{figure}

These should be f1a.eps, f1b.eps, and f1c.eps

\begin{figure}
\plottwo{plotl.eps}{plotr.eps}
\end{figure}

These should be f1a.eps and f1b.eps


Usage:

 ./apjify orig.tex new.tex 

 orig.tex is the original LaTeX file in AASTeX format (well, really it
 only needs to conform to the same style of including figures.  new.tex
 is the desired name for the file whose figures are renamed.  
 

History:

  0.4  if no extension is given in the figure command
       (i.e. \plotone{fig}), then assume that the figures is named
       fig.eps.  This comes up with pdflatex a lot.

  0.3  another catch is that sometimes, a figure that spans multiple
       pages is done through multiple figure environments, with the
       figure number reset via \figurenum{\ref{label}} -- make sure
       that we catch those now.

  0.2  ignore figures that are commented out -- look for a % to the left of
       the plot command

       
Notes:

-- This will not work with two figure groups on the same line:

   \begin{figure}\plotone{pl1.eps}\end{figure}\begin{figure}{pl2.eps}\end{figure}

   It will name them f1a.eps and f1b.eps.  This is simple enough to hack
   around, but I am not sure that anyone ever actually does this.


-- This does not follow \input statements.


-- The extension .eps is used for all files, regardless of whether they are
   EPS files.  This does not seem to cause problems.


-- This does not check to see whether you already have named the some figures
   fn.eps (where n is an integer).  If that is the case, then this might
   overwrite it.  We should actually make a backup copy first.

"""
import string
import os

def getNextLine():
    """ return the next, non-blank line, with everything to the right of the
        comment delimiter, %, removed """
    global lineNum
    global fin
    
    line = fin.readline()
    lineNum += 1

    pos = string.find(line, "%")

    # skip any lines that are all comment
    while (pos == 0):
        line = fin.readline()
        lineNum += 1
        
        pos = string.find(line, "%")
    
    if (pos > 0):
        line = line[:pos]
        
    return line



def getFigureLabel(block):
    """ return the label from the \label{} command in the figure block """
    for line in block:

        indexLabel = string.find(line, "\\label")

        if indexLabel >= 0:
            tempLine = line[indexLabel:]
            indexLB = string.find(tempLine, "{")
            indexRB = string.find(tempLine, "}")            

            label = tempLine[indexLB+1:indexRB]
            return label

    label = ""
    return label
    


def getRenumberLabel(block):
    """ sometimes a figure number is reset, using \figurenum{\ref{label}},
        especially when the figure is multi-page.  Return the label that
        the current figure block refers to. """
    for line in block:

        indexLabel = string.find(line, "\\figurenum")

        if indexLabel >= 0:
            tempLine = line[indexLabel:]
            indexRef = string.find(tempLine, "\\ref")
            temp2Line = tempLine[indexRef:]
            
            indexLB = string.find(temp2Line, "{")
            indexRB = string.find(temp2Line, "}")            

            label = temp2Line[indexLB+1:indexRB]
            return label

    label = ""
    return label
    


def getFigures(block):
    """ return the names of all figures in the current block, in the
        order they are included.  Note -- all figures in the current
        block have by definition the same figure number """

    figures = []
    
    # the list of commands that might be used to include figures in LaTeX
    plotCommands = ["\\plotone", "\\plottwo", "\\includegraphics"]
    numPlotCommands = len(plotCommands)

    # we will keep track of the line in the block where each figure is
    lineCount = 0
    
    for line in block:

        lineData = []
        count = 0
        
        # loop over all possible plot commands
        i = 0
        while (i < numPlotCommands):
            
            # we are going to have to be careful -- there could be more
            # than one instance of a given plot command on each line
            tempLine = line

            index = string.find(tempLine, plotCommands[i])
            while (index >= 0):

                # we found a figure included with the current plot command
                # so extract the name
                tempLine = tempLine[index:]
                indexLB = string.find(tempLine, "{")
                indexRB = string.find(tempLine, "}")

                figure = tempLine[indexLB+1:indexRB]
                tempLine = tempLine[indexRB+1:]
                                                  

                # find the position in the full line of this figure, so we
                # can sort out the order
                pos = string.find(line, figure)

                j = 0
                while j < count:
                    if lineData[j]['pos'] > pos:
                        break

                    j += 1

                count += 1

                # lineData stores all the figures included in the current line
                # in the order that that appear in that line -- regardless of
                # the command used.
                lineData.insert(j,{'pos':pos, 'fig':figure})

                # if we are doing \plottwo, there are two files here
                if (plotCommands[i] == "\\plottwo"):
                    indexLB = string.find(tempLine, "{")
                    indexRB = string.find(tempLine, "}")

                    figure = tempLine[indexLB+1:indexRB]
                    tempLine = tempLine[indexRB+1:]

                    pos = string.find(line, figure)
                    lineData.insert(j+1,{'pos':pos, 'fig':figure})
                    count += 1

                    
                index = string.find(tempLine, plotCommands[i])
                            
            i += 1

        # we are done with the current line, and all the figures in it are
        # in order in lineData -- put them into the main list
        j = 0
        while j < count:
            figures.append({'fig':lineData[j]['fig'],'line':lineCount})
            j += 1

        lineCount += 1
                           
    return figures
    

            
def apjify2(file, outFile, copy):
    
    global lineNum
    global figureIndex
    global fin
    
    if (file == outFile):
        print "ERROR: input and output files are the same"
        return -1

    alpha = "abcdefghijklmnopqrstuvwxyz"
    
    # note -- we assume that each figure command in the begin array
    # is in the same position as its corresponding closing command
    # in the end array.
    beginFigureCommands = ["\\begin{figure}", "\\begin{figure*}"]
    endFigureCommands = ["\\end{figure}", "\\end{figure*}"]
    numFigureCommands = len(endFigureCommands)


    # open up the original file and the output file
    try:
        fin = open(file, 'r')
    except (OSError, IOError), error:
        print error
        return -1


    try:
        fout = open(outFile, 'w')
    except (OSError, IOError), error:
        print error
        return -1


    # blockIndex is the number of the current figure block
    # figureIndex will be the number of the current figure -- in most cases
    # it will be the same as blockIndex, except when \figurenum changes it.
    blockIndex = 0
    figureIndex = 0

    figuresInFile = []
    
    line = getNextLine()


    # begin looking through the file, searching for a figure block
    # surrounded by \begin{figure} ... \end{figure}.  Store the
    # entire block in the list currentBlock.
    while (line):

        i = 0
        while (i < numFigureCommands):
            
            index = string.find(line, beginFigureCommands[i])
            
            if index >= 0:

                # We found a figure block.  Create a list to hold all of the
                # lines in this block, and keep storing them until we find
                # the closing command for this block
                currentBlock = []
                currentBlock.append(line)
                currentBlockStartLine = lineNum
                
                line = getNextLine()

                while (string.find(line, endFigureCommands[i]) < 0):
                    currentBlock.append(line)
                    
                    line = getNextLine()


                # the current line is the closer for this block -- store it
                currentBlock.append(line)
                                
                # first look for the label in this block
                label = getFigureLabel(currentBlock)
                

                # now look to see if this figure is renumbered to point to a
                # previous figures label -- if so figureIndex will be reset
                renumLabel = getRenumberLabel(currentBlock)

                if (renumLabel != ""):
                    j = 0
                    while (j < len(figuresInFile)):
                        if (figuresInFile[j]['label'] == renumLabel):
                            figureIndex = figuresInFile[j]['group']
                            break

                        j += 1
                        
                else:
                    blockIndex += 1


                figureIndex = blockIndex
                    
                
                # now search for all the postscript figures in there 
                figs = getFigures(currentBlock)
                

                # now store each of the figures in the current block
                # in our main list
                j = 0
                while (j < len(figs)):
                    figuresInFile.append({'name':figs[j]['fig'],
                                          'line':figs[j]['line']+currentBlockStartLine,
                                          'label':label,
                                          'group':figureIndex})
                    j += 1
                    
                
                break

            i += 1
            
            
        line = getNextLine()


    # now we have all the figures stored in figuresInFile


    # now that we've identified all the figures, we need to create their
    # new names.  All figures in the same group should have the same
    # integer in the new filename and a letter given in the order they
    # appear in the file (e.g. f5a.eps, f5b.eps, ...).
    currentLetter = 0
    currentGroup = 0
    
    i = 0
    while (i < len(figuresInFile)):
        
        # check to see if we are in the current group.  If not, determine
        # if we need to use letter
        if (figuresInFile[i]['group'] != currentGroup):
            
            currentGroup = figuresInFile[i]['group']
            
            if (i != len(figuresInFile)-1 and \
                figuresInFile[i+1]['group'] == currentGroup):
                
                useLetters = 1
                currentLetter = 0
            else:
                useLetters = 0
                
        if useLetters:
            newFile = 'f' + repr(currentGroup) + alpha[currentLetter] + '.eps'
            currentLetter += 1
        else:
            newFile = 'f' + repr(currentGroup) + '.eps'
                    
        figuresInFile[i]['newname'] = newFile
                    
        i += 1
                    
                    
    # now we need to replace the figures -- we need the line numbers here!!!
    currentIndex = 0
    
    fin.seek(0)
    line = fin.readline()
    lineNum = 1
    
    while (line):
        
        while (lineNum == figuresInFile[currentIndex]['line']):
            
            line = line.replace(figuresInFile[currentIndex]['name'], \
                                figuresInFile[currentIndex]['newname'])
            
            if currentIndex < len(figuresInFile)-1:
                currentIndex += 1
            else:
                break
            
        fout.write(line)
            
        line = fin.readline()
        lineNum += 1
            
            
    # add a log of what we changed to the end of the file
    fout.write("\n\n")
    fout.write("% summary of apjify's changes:\n%\n")
    
    i = 0
    while (i < len(figuresInFile)):
        fout.write("% " + repr(i) + ": renamed " + figuresInFile[i]['name'] + \
                   " to " + figuresInFile[i]['newname'] + \
                   " on line " + repr(figuresInFile[i]['line']) + "\n")
        i += 1

        
    fin.close()
    fout.close()
    
    
    # now do the copies
    i = 0
    while (i < len(figuresInFile)):

        # sometimes, the figure in the file does not have an extension -- this
        # is usually the case for pdflatex.  We'll assume that it is a .eps
        # extension.
        if (string.find(figuresInFile[i]['name'], ".") < 0):
            copyCommand = "cp " + figuresInFile[i]['name'] + ".eps " + figuresInFile[i]['newname']
            os.system(copyCommand)
            
        else:
            copyCommand = "cp " + figuresInFile[i]['name'] + " " + figuresInFile[i]['newname']
            os.system(copyCommand)
        
        i += 1
        
    return 1


            
if __name__=="__main__":

    import sys
        
    if len(sys.argv) != 3:
        print 'usage: apjify.py orig.tex new.tex'
        sys.exit()
        
    origFile = sys.argv[1]
    newFile = sys.argv[2]
    copy = 1
    
    apjify2(origFile, newFile, copy)
  
