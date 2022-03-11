# Create OCR layers for all files except one buggy one
for i in $(ls -1 | grep -v '1996_the_supreme_court')
do
    echo $i;
    ocrmypdf --output-type pdf --skip-text $i $i
done 

# Convert PDF files to text ones
for i in *
do
    echo $i
    pdf2txt.py $i -A --outfile ${i/pdf/txt}
done 