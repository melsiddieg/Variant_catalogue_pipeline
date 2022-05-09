#!/usr/bin/env python
# coding: utf-8

# Hail and plot initialisation

# In[91]:


import hail as hl
from hail.plot import output_notebook, show
hl.init()
output_notebook()

import sys

# In[ ]:


from hail.plot import show
from pprint import pprint
from bokeh.models import Span
hl.plot.output_notebook()
from bokeh.models import Range1d
from bokeh.plotting import figure, output_file, show, save
from bokeh.io import export_png

import pandas as pd
import os


# Import a vcf file and read it as a matrix table (mt, hail specific file type)
# For specific on how to look at the mt file, refer to the bottom of this Jupyter notebook)

# In[ ]:

hl.import_vcf(sys.argv[1], array_elements_required=False, force_bgz=True).write('SNV_vcf.mt', overwrite=True)


#vcf_path = '/mnt/scratch/SILENT/Act3/Processed/Individual/GRCh37/Batch_DryRun/Run_20220426/vcf_pre_hail/'

#hl.import_vcf(os.path.join(vcf_path,'DeepVariant_GLnexus_Run_20220426.vcf.gz'),
#              array_elements_required=False, force_bgz=True).write('SNV_vcf.mt', overwrite=True)


# For MT, need to find a different technique as it is not a diploiod genome
# 
# 
# Error summary: VCFParseError: ploidy > 2 not supported

# hl.import_vcf(os.path.join(vcf_path,'MT_Run_20220426.vcf.gz'), 
#               array_elements_required=False, force_bgz=True,
#               reference_genome='GRCh38').write('hail/MT_vcf.mt', overwrite=True)

# In[ ]:


SNV_mt = hl.read_matrix_table('SNV_vcf.mt')


# The vcf should be merged into one vcf to avoid redundancy (Possible calling overlap for indel witht he deepvaraint and SV pipeline)

# In order to create the graph, 3 functions were needed
# - stat : To calcualte the mean, standard deviation and other metrics for each parameter
# - plot_histo : To create the histogram as expected
# - plot_sp : To create the scatter plots as expected

# In[ ]:


def stat(table):
    Mean = table[table.columns[1]]. mean()  
    StdDev = table[table.columns[1]]. std()
    Low_threashold = Mean - 3*StdDev
    High_threashold = Mean + 3*StdDev
    min_graph = table[table.columns[1]]. min() - 3*StdDev
    max_graph = table[table.columns[1]]. max() + 3*StdDev
    return Mean, StdDev, Low_threashold, High_threashold, min_graph, max_graph


# In[106]:


def plot_histo (table_plot, mt_plot, variable) :
    output_file(filename=("sample_QC_"+variable+".html"), title="Sample QC HTML file")
    p = hl.plot.histogram(mt_plot,
                      range = (stat(table_plot) [4], stat(table_plot) [5]),
                      bins = 60,
                      legend=variable,
                      title="Red lines are Mean +/- 3xStdDev")
    annot = Span(dimension="height",location=stat(table_plot) [2],line_dash='dashed', line_width=3,line_color="red")
    p.add_layout(annot)
    annot2 = Span(dimension="height",location=stat(table_plot) [3],line_dash='dashed', line_width=3,line_color="red")
    p.add_layout(annot2)
    p.yaxis.axis_label = 'Count'
    return save(p)


# In[107]:


def plot_sp (table_x_axis, mt_x_axis, table_y_axis, mt_y_axis, x_variable, y_variable) :
    output_file(filename=("sample_QC_"+x_variable+"_"+y_variable+".html"), title="Sample QC HTML file")
    p = hl.plot.scatter(x=mt_x_axis,
                   y=mt_y_axis,
                  xlabel=x_variable,
                  ylabel=y_variable,
                title="Red lines are Mean +/- 3xStdDev",
                  hover_fields={'ID':SNV_mt_sample_qc.s},
                  size=5)
    annot = Span(dimension="height",location=stat(table_x_axis) [2],line_dash='dashed', line_width=3,line_color="red")
    annot2 = Span(dimension="height",location=stat(table_x_axis) [3],line_dash='dashed', line_width=3,line_color="red")
    annot3 = Span(dimension="width",location=stat(table_y_axis) [2],line_dash='dashed', line_width=3,line_color="red")
    annot4 = Span(dimension="width",location=stat(table_y_axis) [3],line_dash='dashed', line_width=3,line_color="red")
    p.add_layout(annot)
    p.add_layout(annot2)
    p.add_layout(annot3)
    p.add_layout(annot4)
    p.x_range=Range1d(stat(table_x_axis) [4], stat(table_x_axis) [5])
    p.y_range=Range1d(stat(table_y_axis) [4], stat(table_y_axis) [5])
    return save(p)


# **Generate the sample quality control metrics using hail**

# In[ ]:


SNV_mt_sample_qc = hl.sample_qc(SNV_mt)


# List the sample quality control metric that were generated by hail

# In[ ]:


SNV_mt_sample_qc.describe()


# Create plots for sample QC
# 
# Following the lab meeting, it was decided to define the threasholds based on the standard deviations and no hard filters. This will allow to identify outliers without relying on gnomAD values.
# 
# The Standard deviation is available thourgh the summarize function, but I cannot figure out how to extract the value. I can't figure ouot how to create a pd DataFrame from Hail matric neither (to_Pandas() is not working). Solution : Save the file with values as a csv and reopen it, calculate the Std Dev based on this.

# List of variables for which we will create a table, calculate the standard deviation (StdDev) and the mean (Mean) for sample QC:
# - DP (mt_sample_qc.sample_qc.dp_stats.mean)
# - QG (mt_sample_qc.sample_qc.gq_stats.mean)
# - call_rate (mt_sample_qc.sample_qc.call_rate)
# - r_het_hom_var (mt_sample_qc.sample_qc.r_het_hom_var)
# - n_het (mt_sample_qc.sample_qc.n_het)
# - n_hom_var (mt_sample_qc.sample_qc.n_hom_var)
# - n_snp (mt_sample_qc.sample_qc.n_snp)
# - n_singleton (mt_sample_qc.sample_qc.n_singleton)
# - r_insertion_deletion (mt_sample_qc.sample_qc.r_insertion_deletion)
# - n_insertion (mt_sample_qc.sample_qc.n_insertion)
# - n_deletion (mt_sample_qc.sample_qc.n_deletion)
# - r_ti_tv (mt_sample_qc.sample_qc.r_ti_tv)
# - n_transition (mt_sample_qc.sample_qc.n_transition)
# - n_transversion (mt_sample_qc.sample_qc.n_transversion)

# Save the values as table

# In[ ]:


SNV_mt_sample_qc.sample_qc.dp_stats.mean.export('vcf_to_try_hail/11samples/DP.tsv')
SNV_mt_sample_qc.sample_qc.gq_stats.mean.export('vcf_to_try_hail/11samples/GQ.tsv')
SNV_mt_sample_qc.sample_qc.call_rate.export('vcf_to_try_hail/11samples/call_rate.tsv')
SNV_mt_sample_qc.sample_qc.r_het_hom_var.export('vcf_to_try_hail/11samples/r_het_hom_var.tsv')
SNV_mt_sample_qc.sample_qc.n_het.export('vcf_to_try_hail/11samples/n_het.tsv')
SNV_mt_sample_qc.sample_qc.n_hom_var.export('vcf_to_try_hail/11samples/n_hom_var.tsv')
SNV_mt_sample_qc.sample_qc.n_snp.export('vcf_to_try_hail/11samples/n_snp.tsv')
SNV_mt_sample_qc.sample_qc.n_singleton.export('vcf_to_try_hail/11samples/n_singleton.tsv')
SNV_mt_sample_qc.sample_qc.r_insertion_deletion.export('vcf_to_try_hail/11samples/r_insertion_deletion.tsv')
SNV_mt_sample_qc.sample_qc.n_insertion.export('vcf_to_try_hail/11samples/n_insertion.tsv')
SNV_mt_sample_qc.sample_qc.n_deletion.export('vcf_to_try_hail/11samples/n_deletion.tsv')
SNV_mt_sample_qc.sample_qc.r_ti_tv.export('vcf_to_try_hail/11samples/r_ti_tv.tsv')
SNV_mt_sample_qc.sample_qc.n_transition.export('vcf_to_try_hail/11samples/n_transition.tsv')
SNV_mt_sample_qc.sample_qc.n_transversion.export('vcf_to_try_hail/11samples/n_transversion.tsv')


# Open the tables as data frame

# In[ ]:


DP_table=pd.read_table('vcf_to_try_hail/11samples/DP.tsv')
GQ_table=pd.read_table('vcf_to_try_hail/11samples/GQ.tsv')
call_rate_table=pd.read_table('vcf_to_try_hail/11samples/call_rate.tsv')
r_het_hom_var_table=pd.read_table('vcf_to_try_hail/11samples/r_het_hom_var.tsv')
n_het_table=pd.read_table('vcf_to_try_hail/11samples/n_het.tsv')
n_hom_var_table=pd.read_table('vcf_to_try_hail/11samples/n_hom_var.tsv')
n_snp_table=pd.read_table('vcf_to_try_hail/11samples/n_snp.tsv')
n_singleton_table=pd.read_table('vcf_to_try_hail/11samples/n_singleton.tsv')
r_insertion_deletion_table=pd.read_table('vcf_to_try_hail/11samples/r_insertion_deletion.tsv')
n_insertion_table=pd.read_table('vcf_to_try_hail/11samples/n_insertion.tsv')
n_deletion_table=pd.read_table('vcf_to_try_hail/11samples/n_deletion.tsv')
r_ti_tv_table=pd.read_table('vcf_to_try_hail/11samples/r_ti_tv.tsv')
n_transition_table=pd.read_table('vcf_to_try_hail/11samples/n_transition.tsv')
n_transversion_table=pd.read_table('vcf_to_try_hail/11samples/n_transversion.tsv')


# Rename the column of the tables

# In[ ]:


DP_table.rename(columns = {DP_table.columns[1]:'DP'}, inplace = True)
GQ_table.rename(columns = {GQ_table.columns[1]:'GQ'}, inplace = True)
call_rate_table.rename(columns = {call_rate_table.columns[1]:'call_rate'}, inplace = True)
r_het_hom_var_table.rename(columns = {r_het_hom_var_table.columns[1]:'r_het_hom_var'}, inplace = True)
n_het_table.rename(columns = {n_het_table.columns[1]:'n_het'}, inplace = True)
n_hom_var_table.rename(columns = {n_hom_var_table.columns[1]:'n_hom_var'}, inplace = True)
n_snp_table.rename(columns = {n_snp_table.columns[1]:'n_snp'}, inplace = True)
n_singleton_table.rename(columns = {n_singleton_table.columns[1]:'n_singleton'}, inplace = True)
r_insertion_deletion_table.rename(columns = {r_insertion_deletion_table.columns[1]:'r_insertion_deletion'}, inplace = True)
n_insertion_table.rename(columns = {n_insertion_table.columns[1]:'n_insertion'}, inplace = True)
n_deletion_table.rename(columns = {n_deletion_table.columns[1]:'n_deletion'}, inplace = True)
r_ti_tv_table.rename(columns = {r_ti_tv_table.columns[1]:'r_ti_tv'}, inplace = True)
n_transition_table.rename(columns = {n_transition_table.columns[1]:'n_transition'}, inplace = True)
n_transversion_table.rename(columns = {n_transversion_table.columns[1]:'n_transversion'}, inplace = True)


# Create the graphs

# In[108]:


plot_histo(DP_table, SNV_mt_sample_qc.sample_qc.dp_stats.mean, 'Mean Depth per sample')


# In[109]:


plot_histo(GQ_table,
           SNV_mt_sample_qc.sample_qc.gq_stats.mean,
           'Mean Genotype quality per sample')


# In[110]:


plot_histo(call_rate_table,
           SNV_mt_sample_qc.sample_qc.call_rate,
           'Call Rate per sample')


# In[111]:


plot_histo(r_het_hom_var_table,
           SNV_mt_sample_qc.sample_qc.r_het_hom_var,
           'Ratio heterozygous to homozygous variants per sample')


# In[112]:


plot_sp (n_het_table,
         SNV_mt_sample_qc.sample_qc.n_het,
         n_hom_var_table,
         SNV_mt_sample_qc.sample_qc.n_hom_var,
         'Number of Heterozygous Variants',
         'Number of homozygous variants')


# In[113]:


plot_histo(n_snp_table,
           SNV_mt_sample_qc.sample_qc.n_snp,
           'Number of SNPs per sample')


# In[114]:


n_singleton_table


# In[115]:


plot_histo(n_singleton_table,
           SNV_mt_sample_qc.sample_qc.n_singleton,
           'Number of singletons per sample')


# In[116]:


plot_sp (n_insertion_table,
         SNV_mt_sample_qc.sample_qc.n_insertion,
         n_deletion_table,
         SNV_mt_sample_qc.sample_qc.n_deletion,
         'Number of insertions',
         'Number of deletions')


# In[117]:


plot_histo(r_insertion_deletion_table,
           SNV_mt_sample_qc.sample_qc.r_insertion_deletion,
           'Ratio insertions to deletions per sample')


# In[118]:


plot_sp (n_transition_table,
         SNV_mt_sample_qc.sample_qc.n_transition,
         n_transversion_table,
         SNV_mt_sample_qc.sample_qc.n_transversion,
         'Number of transitions',
         'Number of transversions')


# In[119]:


plot_histo(r_ti_tv_table,
           SNV_mt_sample_qc.sample_qc.r_ti_tv,
           'Ratio transitions to transversions per sample')


# In[ ]:





# In[ ]:





# **Filter the samples based on the threasholds repersented on the figures**
# 
# On the test with 11 samples, no samples shoould be removed
# 
# Low_threashold = Mean - 3*StdDev = stat(table) [2]
# 
# High_threashold = Mean + 3*StdDev = stat(table) [3]
# 
# Filters :
# - Mean DP per sample lower than the low threshoold
# - Mean Genotype Quality per sample lower than the low threshoold
# - Mean call rate per sample lower than the low threshoold
# - Ratio heterozygous to homozygous variants per sample lower than the low threshoold or higher than high threshold
# - Number of SNPs per sample lower than the low threshoold or higher than high threshold
# - Number of singletons per sample lower than the low threshoold or higher than high threshold
# - ?? Ratio insertions to deletion per sample lower than the low threshoold or higher than high threshold
# - Ratio transition to transversions per sample lower than the low threshoold or higher than high threshold

# In[120]:


filtered_SNV_mt_sample_qc_samples = SNV_mt_sample_qc.filter_cols((SNV_mt_sample_qc.sample_qc.dp_stats.mean > stat(DP_table) [2]) &
                                                                 (SNV_mt_sample_qc.sample_qc.gq_stats.mean > stat(GQ_table) [2]) &
                                                                 (SNV_mt_sample_qc.sample_qc.call_rate > stat(call_rate_table) [2]) &
                                                                 (stat(r_het_hom_var_table) [3] > SNV_mt_sample_qc.sample_qc.r_het_hom_var) &
                                                                 (SNV_mt_sample_qc.sample_qc.r_het_hom_var > stat(r_het_hom_var_table) [2]) &
                                                                 (stat(n_snp_table) [3] > SNV_mt_sample_qc.sample_qc.n_snp) &
                                                                 (SNV_mt_sample_qc.sample_qc.n_snp > stat(n_snp_table) [2]) &
                                                                 (stat(n_singleton_table) [3] > SNV_mt_sample_qc.sample_qc.n_singleton) &
                                                                 (SNV_mt_sample_qc.sample_qc.n_singleton > stat(n_singleton_table) [2]) &
                                                                 (stat(r_insertion_deletion_table) [3] > SNV_mt_sample_qc.sample_qc.r_insertion_deletion) &
                                                                 (SNV_mt_sample_qc.sample_qc.r_insertion_deletion > stat(r_insertion_deletion_table) [2]) &
                                                                 (stat(r_ti_tv_table) [3] > SNV_mt_sample_qc.sample_qc.r_ti_tv) &
                                                                 (SNV_mt_sample_qc.sample_qc.r_ti_tv> stat(r_ti_tv_table) [2])
                                                                )


# In[124]:


hl.export_vcf(filtered_SNV_mt_sample_qc_samples, 'filtered_samples.vcf.bgz')


# In[ ]:


SNV_mt_sample_qc.count()


# In[ ]:


filtered_SNV_mt_sample_qc_samples.count()


# In[ ]:


perc_removed_samples = (SNV_mt_sample_qc.count()[0]-filtered_SNV_mt_sample_qc_samples.count()[0])/SNV_mt_sample_qc.count()[0] * 100


# In[ ]:


print("%.2f %% of the samples were filtered out." % perc_removed_samples)
