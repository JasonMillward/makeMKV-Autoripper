"""
"""
import os
import commands


class handbrake(object):

    """ Function:   _cleanUp
            Removes the log file and the input movie because these files are
                no longer needed by this script

        Inputs:
            log         (Str): File path of the log to remove
            oldMovie    (Str): File path of the movie to remove

        Outputs:
            None
    """
    def _cleanUp(log, oldMovie):
        os.remove(log)
        os.remove(oldMovie)

    """ Function:   _updateQueue
            Removes the recently processed movie from the queue so it's not
                processed again

        Inputs:
            None

        Outputs:
            None
    """
    def _updateQueue(self):
        f = open("%s/.makemkvautoripper/queue" % self.home, "w")
        for line in self.lines:
            if (self.movie not in line):
                f.write(line)

        f.write("\n")
        f.close()

    """ Function:   _cleanQueue

        Inputs:
            None

        Outputs:
            None
    """
    def _cleanQueue(self):
        try:
            f = open("%s/.makemkvautoripper/queue" % self.home, "r")
            lines = f.readlines()
            f.close()
        except:
            print "Could not read queue file"

        f = open("%s/.makemkvautoripper/queue" % self.home, "w")

        for line in lines:
            if (line != "\n"):
                f.write(line)

        f.write("\n")
        f.close()

    """ Function:   findProcess


        Inputs:
            None

        Outputs:
            None
    """
    def findProcess(self):
        processname = 'HandBrakeCLI'
        for line in os.popen("ps xa"):
            fields = line.split()
            process = fields[4]
            if process.find(processname) >= 0:
                return True
                break

        return False

    """ Function:   loadMovie


        Inputs:
            None

        Outputs:
            None
    """
    def loadMovie(self):
        try:
            self.home = os.path.expanduser("~")
            self._cleanQueue()

            if os.path.isfile("%s/.makemkvautoripper/queue" % self.home):
                f = open("%s/.makemkvautoripper/queue" % self.home, "r")
                self.lines = f.readlines()
                f.close()

                movie = self.lines[0].replace("\n", "")
                movie = movie.split('|')

                self.path = movie[0]
                self.movie = movie[1]
                self.inputMovie = movie[2]
                self.outputMovie = movie[3]

                return True
            else:
                return False
        except:
            return False

    """ Function:   convert
            Passes the nessesary parameters to HandBrake to start an encoding
            Assigns a nice value to allow give normal system tasks priority

            Upon successful encode, clean up the output logs and remove the
                input movie as they are no longer needed

        Inputs:
            nice    (Int): Priority to assign to task (nice value)
            args    (Str): All of the handbrake arguments taken from the
                            settings file
            output  (Str): File to log to. Used to see if the job completed
                            successfully

        Outputs:
            None
    """
    def convert(self, nice, args, output):
        path = "%s/%s" % (self.path, self.movie)
        inMovie = "%s/%s" % (path, self.inputMovie)
        outMovie = "%s/%s" % (path, self.outputMovie)

        print "Converting..."
        commands.getstatusoutput(
            'nice -n %d HandBrakeCLI --verbose 1 -i "%s" -o "%s" %s 2> %s'
            %
            (nice, inMovie, outMovie, args, output))

        checks = 0
        try:
            tempFile = open(output, 'r')
            for line in tempFile.readlines():
                if "average encoding speed for job" in line:
                    checks += 1
                if "Encode done!" in line:
                    checks += 1
        except:
            print "Could not read output file, no cleanup will be done"

        if checks == 0:
            self._updateQueue()
            self._cleanUp(log=output, oldMovie=inMovie)
