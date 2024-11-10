import pandas as pd

def join_csv(main_csv, *other_csvs):
  """
  Performs a right join of the last column of the main CSV onto other CSVs.

  Args:
    main_csv: Path to the main CSV file.
    *other_csvs: Paths to the other CSV files to be joined.
  """
  try:
    # Load the main CSV file
    df_main = pd.read_csv(main_csv)

    # Extract the last column from the main CSV
    last_column_main = df_main.iloc[:, -1]

    # Iterate through the other CSV files
    for csv_file in other_csvs:
      # Load the current CSV file
      df_other = pd.read_csv(csv_file)

      # Perform the right join
      df_joined = pd.concat([df_other, last_column_main], axis=1)

      # Save the joined DataFrame (optional - you can modify the output filename)
      output_filename = csv_file.replace('.csv', '_joined.csv')
      df_joined.to_csv(output_filename, index=False)
      print(f"Joined data saved to: {output_filename}")

  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  main_csv_file = './landslide/landslide_raw.csv'  # Replace with your main CSV file name
  other_csv_files = ['./flood/edges_i_j_10yr.csv', './flood/edges_i_j_20yr.csv', './flood/edges_i_j_50yr.csv']  # Replace with your other CSV file names
  join_csv(main_csv_file, *other_csv_files)