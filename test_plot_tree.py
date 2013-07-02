import mergertrees.MTCatalogue as mtc
import subprocess
mt = mtc.MTCatalogue("/spacebase/data/AnnaGroup/caterpillar/parent/RockstarData/trees",numHosts=1)
mt[0].plottree('tree0')
subprocess.call(["display","tree0.pdf"])
