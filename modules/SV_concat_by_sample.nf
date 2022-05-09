// Nextflow process
// Owned by the Silent Genomes Project Activity 3 team
// Developped to build the IBVL, a background variant library

// Overview of the process goal and characteristics :
// SV calling. Concatenante the SVs called by different callers for each sample



process SV_concat_by_sample {
	tag "${sample_name}"

	publishDir "$params.outdir_ind/${assembly}/${batch}/${run}/SV/Concat_by_sample", mode: 'copy'

	input:
        tuple(path(vcfs), path(indexes), val(sample_name))
	val assembly
	val batch
	val run	

	output:
	file("${output_file}")

	script:
	output_file = "${sample_name}.concat-svs.vcf"
	"""
	bcftools concat -a -O v -o ${output_file} *.vcf.gz
	"""
}
