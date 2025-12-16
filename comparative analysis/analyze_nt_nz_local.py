"""
NT → NZ Conversion Analysis
For use on local machine with historic new .xlsx file

Instructions:
1. Make sure openpyxl is installed: pip install openpyxl
2. Place 'historic new .xlsx' in the same folder as this script
3. Run: python analyze_nt_nz_local.py
"""

import pandas as pd
import numpy as np

print("="*80)
print("NT → NZ CONVERSION TRACKER (2021-2025)")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n📂 Loading data...")

try:
    df = pd.read_excel('historic new .xlsx', sheet_name='sbti evolution ')
    df.columns = df.columns.str.strip()
    print(f"✅ Loaded {len(df)} companies from Excel file")
except FileNotFoundError:
    print("❌ Error: Could not find 'historic new .xlsx'")
    print("   Make sure the file is in the same folder as this script")
    exit()
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit()

years = ['2021', '2022', '2023', '2024', '2025']

# ============================================================================
# BUILD PROGRESSION TRACKER
# ============================================================================
print("\n🔄 Building progression tracker...")

progressions = []

for idx, row in df.iterrows():
    company = row['company']
    record = {'Company': company}
    
    # Extract status for each year
    for year in years:
        nt_status = row.get(f'{year}_NT_Status', np.nan)
        nz_status = row.get(f'{year}_NZ_Status', np.nan)
        
        record[f'NT_{year}'] = nt_status if pd.notna(nt_status) else 'None'
        record[f'NZ_{year}'] = nz_status if pd.notna(nz_status) else 'None'
    
    # Find first year with NT
    first_nt_year = None
    for year in years:
        if record[f'NT_{year}'] not in ['None', 'nan']:
            first_nt_year = year
            break
    
    # Find first year with NZ
    first_nz_year = None
    for year in years:
        if record[f'NZ_{year}'] not in ['None', 'nan']:
            first_nz_year = year
            break
    
    record['First_NT_Year'] = first_nt_year
    record['First_NZ_Year'] = first_nz_year
    
    # Calculate pathway
    if first_nt_year and first_nz_year:
        nt_num = int(first_nt_year)
        nz_num = int(first_nz_year)
        years_gap = nz_num - nt_num
        
        if years_gap > 0:
            record['Pathway'] = 'NT first → NZ later'
            record['Years_Between'] = years_gap
        elif years_gap == 0:
            record['Pathway'] = 'NT and NZ same year'
            record['Years_Between'] = 0
        else:
            record['Pathway'] = 'NZ first → NT later'
            record['Years_Between'] = abs(years_gap)
    elif first_nt_year and not first_nz_year:
        record['Pathway'] = 'NT only (no NZ)'
        record['Years_Between'] = np.nan
    elif first_nz_year and not first_nt_year:
        record['Pathway'] = 'NZ only (no NT)'
        record['Years_Between'] = np.nan
    else:
        record['Pathway'] = 'No commitment'
        record['Years_Between'] = np.nan
    
    progressions.append(record)

progression_df = pd.DataFrame(progressions)

# Save results
output_file = 'nt_nz_conversion_results.csv'
progression_df.to_csv(output_file, index=False)
print(f"✅ Saved detailed results to: {output_file}")

# ============================================================================
# ANALYSIS 1: PATHWAY DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("PATHWAY DISTRIBUTION")
print("="*80)

pathway_counts = progression_df['Pathway'].value_counts()
print("\n📊 How do companies progress from NT to NZ?\n")

for pathway, count in pathway_counts.items():
    pct = (count / len(progression_df)) * 100
    print(f"   {pathway:.<45} {count:>4} ({pct:>5.1f}%)")

# ============================================================================
# ANALYSIS 2: NT → NZ CONVERSION
# ============================================================================
print("\n" + "="*80)
print("NT → NZ CONVERSION ANALYSIS")
print("="*80)

nt_first = progression_df[progression_df['Pathway'] == 'NT first → NZ later']
print(f"\n✅ Companies that got NT first, then added NZ: {len(nt_first)}")

if len(nt_first) > 0:
    avg_gap = nt_first['Years_Between'].mean()
    
    print(f"\n⏱️  Average time from NT to NZ: {avg_gap:.2f} years")
    
    # Distribution
    print(f"\n📊 Time gap distribution:")
    gap_dist = nt_first['Years_Between'].value_counts().sort_index()
    for gap, count in gap_dist.items():
        pct = (count / len(nt_first)) * 100
        bar = '█' * int(pct / 2)
        print(f"   {gap:.0f} year(s):  {count:>3} ({pct:>5.1f}%)  {bar}")
    
    # Examples
    print(f"\n🔍 Top 15 examples:\n")
    print(f"   {'Company':<40} {'NT Year':<10} {'NZ Year':<10} {'Gap':<5}")
    print(f"   {'-'*70}")
    
    for idx, row in nt_first.sort_values('Years_Between').head(15).iterrows():
        print(f"   {row['Company']:<40} {row['First_NT_Year']:<10} {row['First_NZ_Year']:<10} {row['Years_Between']:<5.0f}")

# ============================================================================
# ANALYSIS 3: SAME YEAR COMMITMENTS
# ============================================================================
print("\n" + "="*80)
print("SIMULTANEOUS NT AND NZ COMMITMENTS")
print("="*80)

same_year = progression_df[progression_df['Pathway'] == 'NT and NZ same year']
print(f"\n✅ Companies that set both NT and NZ together: {len(same_year)}")

if len(same_year) > 0:
    year_dist = same_year['First_NT_Year'].value_counts().sort_index()
    print(f"\n📅 By year:")
    for year, count in year_dist.items():
        pct = (count / len(same_year)) * 100
        print(f"   {year}: {count:>3} companies ({pct:.1f}%)")

# ============================================================================
# ANALYSIS 4: CONVERSION BY COHORT
# ============================================================================
print("\n" + "="*80)
print("CONVERSION RATE BY COHORT")
print("="*80)

print("\n📊 For companies that got NT in year X, what % have NZ by 2025?\n")

for start_year in years:
    cohort = progression_df[progression_df['First_NT_Year'] == start_year]
    
    if len(cohort) > 0:
        # How many have NZ?
        has_nz = cohort[cohort['First_NZ_Year'].notna()]
        
        conversion_rate = (len(has_nz) / len(cohort)) * 100
        years_elapsed = 2025 - int(start_year)
        
        print(f"   {start_year} cohort ({years_elapsed} years elapsed):")
        print(f"      Started with NT: {len(cohort)}")
        print(f"      Have NZ: {len(has_nz)}")
        print(f"      Conversion rate: {conversion_rate:.1f}%")
        print()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("="*80)
print("SUMMARY STATISTICS")
print("="*80)

total_companies = len(progression_df)
ever_had_nt = len(progression_df[progression_df['First_NT_Year'].notna()])
ever_had_nz = len(progression_df[progression_df['First_NZ_Year'].notna()])
have_both = len(progression_df[
    (progression_df['First_NT_Year'].notna()) & 
    (progression_df['First_NZ_Year'].notna())
])

overall_conversion = (have_both / ever_had_nt * 100) if ever_had_nt > 0 else 0

print(f"""
📊 Key Metrics:

   Total companies tracked: {total_companies}
   
   EVER had Near-term SBTi: {ever_had_nt} ({ever_had_nt/total_companies*100:.1f}%)
   EVER had Net Zero: {ever_had_nz} ({ever_had_nz/total_companies*100:.1f}%)
   EVER had BOTH: {have_both} ({have_both/total_companies*100:.1f}%)
   
   🎯 Overall NT → NZ Conversion Rate: {overall_conversion:.1f}%
   
   Pathway breakdown:
      • NT first → NZ later: {len(nt_first)}
      • NT and NZ same year: {len(same_year)}
      • NT only (no NZ): {len(progression_df[progression_df['Pathway'] == 'NT only (no NZ)'])}
      
   ⏱️  Average time from NT to NZ: {avg_gap if len(nt_first) > 0 else 0:.1f} years
""")

print("="*80)
print("✅ ANALYSIS COMPLETE")
print("="*80)
print(f"\n📁 Results saved to: {output_file}")
print("\nYou can open this CSV file in Excel to explore the data further!\n")
