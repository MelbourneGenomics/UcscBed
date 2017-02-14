------------
Introduction
------------

UCSC Bed is a module for creating a BED file out of the UCSC refseq genes list. It is able to connect to, download, and
process the genes list from the UCSC ftp site for any reference genome.

------------
Installation
------------
Just run :code:`pip install ucsc_bed`

---
CLI
---
Use :code:`ucsc_bed REFERENCE --email EMAIL > exons.bed`, where :code:`REFERENCE` is the name of the genome build you want a bed file for
(e.g. `hg19`, `hg38` etc.), and :code:`EMAIL` is your email address that is used when logging onto the UCSC FTP site (you don't require
registration)

---
API
---
You can also access the bed file in python like this:

.. code:: python
	import ucsc_bed

	bed_str = ucsc_bed.download_table('hg38', 'email@email.com')
	print(bed_str)


