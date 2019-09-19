import tempfile
import subprocess

f = tempfile.NamedTemporaryFile(delete=False)

f.write(b'jdfbgjkh')
f.close()

n = f.name

subprocess.call(['nano', n])

print 'is done'