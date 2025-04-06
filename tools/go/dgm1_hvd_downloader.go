package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"sync"
)

// FeatureCollection represents the top-level structure of the GeoJSON file
type FeatureCollection struct {
	Features []Feature `json:"features"`
}

// Feature represents a single feature in the GeoJSON file
type Feature struct {
	Properties Properties `json:"properties"`
}

// Properties contains the metadata for each feature
type Properties struct {
	LinkData string `json:"link_data"`
	Kachel   string `json:"kachel"`
	Datum    string `json:"datum"`
}

var (
	gWorkerCount  int
	gInputPath    string
	gOutputDir    string
	gLogPath      string
	gMinFileSize  int64
	gStart        int64
	gEnd          int64
	gDownloadMode bool
	gVerifyMode   bool
)

func main() {

	// Get the current working directory (from where the program was launched)
	cwd, err := os.Getwd()
	if err != nil {
		fmt.Println("Error getting current working directory:", err)
		return
	}

	defaultLogPath := filepath.Join(cwd, "missing_or_small_files.log")
	defaultDownloadPath := filepath.Join(cwd, "downloads")
	//"/Volumes/RoaldMedia2/DGM1_SH__Massendownload.geojson"
	// Define command-line flags
	flag.StringVar(&gInputPath, "in", "", "Input file path with JSON feature collection ")
	flag.StringVar(&gOutputDir, "out", "/downloads", "Output directory path for downloaded files")
	flag.StringVar(&gLogPath, "log", defaultLogPath, "Path to the log file")
	flag.Int64Var(&gMinFileSize, "minsize", 10000, "Minimum file size in bytes to be considered valid")
	flag.BoolVar(&gDownloadMode, "download", false, "Download mode")
	flag.BoolVar(&gVerifyMode, "verify", false, "Verify mode")

	// Optional flags
	flag.IntVar(&gWorkerCount, "workers", 1, "Optional number of workers (-1 for automatic detection)")
	flag.Int64Var(&gStart, "start", 0, "Optional index to start downloading from")
	flag.Int64Var(&gEnd, "end", -1, "Optional index to stop downloading at (-1 for all)")
	gHelp := flag.Bool("help", false, "Show usage information")

	// Parse the flags
	flag.Parse()

	if *gHelp {
		flag.Usage()
		return
	}

	// Validate that Mode is a single character
	if !gDownloadMode && !gVerifyMode {
		fmt.Println("Error: Unknown mode, use -download or -verify")
		return
	}

	// Ensure gOutputDir is not empty
	if len(gInputPath) < 1 {
		fmt.Println("Error: input (-in) is required.")
		return
	}

	// Ensure gOutputDir is not empty
	if gOutputDir == "" {
		fmt.Println("Error: Output directory (-out) is required.")
		return
	}

	// Cap the number of workers
	maxWorkers := runtime.NumCPU() * 2
	if gWorkerCount > maxWorkers {
		gWorkerCount = maxWorkers
	}

	fmt.Println("defaultLogPath", defaultLogPath)
	fmt.Println("defaultDownloadPath", defaultDownloadPath)

	fmt.Println("gDownloadMode", gDownloadMode)
	fmt.Println("gVerifyMode", gVerifyMode)
	fmt.Println("gInputPath", gInputPath)
	fmt.Println("gOutputDir", gOutputDir)
	fmt.Println("gLogPath", gLogPath)
	fmt.Println("gMinFileSize", gMinFileSize)
	fmt.Println("gStart", gStart)
	fmt.Println("gEnd", gEnd)

	// Open the GeoJSON file
	file, err := os.Open(gInputPath)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	// Decode the JSON
	var geojson FeatureCollection
	decoder := json.NewDecoder(file)
	err = decoder.Decode(&geojson)
	if err != nil {
		fmt.Println("Error decoding JSON:", err)
		return
	}

	if gVerifyMode {
		err = checkDownloadedFiles(geojson.Features[gStart:], gMinFileSize, gLogPath)
		if err != nil {
			fmt.Println("Error during file check:", err)
		} else {
			fmt.Println("File scan complete. Log written to:", gLogPath)
		}
		return
	}

	if gDownloadMode {

		// Create job queue and WaitGroup
		jobs := make(chan Feature, len(geojson.Features))
		var wg sync.WaitGroup

		// Start worker goroutines
		for i := 0; i < gWorkerCount; i++ {
			go worker(jobs, &wg)
		}

		// Send jobs to the channel
		for index, feature := range geojson.Features {
			// Skip indices before startIndex
			if int64(index) < gStart {
				continue
			}

			// Stop if we reach endIndex
			if gEnd != -1 && int64(index) > gEnd {
				break
			}

			fmt.Println("index:", index)
			wg.Add(1)
			jobs <- feature
		}

		close(jobs) // Close the job queue when done
		wg.Wait()   // Wait for all downloads to finish
	}
}

// worker function processes the download jobs
func worker(jobs <-chan Feature, wg *sync.WaitGroup) {
	for feature := range jobs {
		url := feature.Properties.LinkData
		filename := generateFilename(feature)

		fmt.Println("Downloading:", url)
		err := downloadFile(url, filename)
		if err != nil {
			fmt.Println("Error downloading", filename, ":", err)
		} else {
			fmt.Println("Downloaded:", filename)
		}
		wg.Done()
	}
}

// downloadFile downloads a file from the given URL and saves it locally
func downloadFile(url, filename string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to download file, status: %s", resp.Status)
	}

	outFile, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer outFile.Close()

	_, err = io.Copy(outFile, resp.Body)
	return err
}

// checkDownloadedFiles scans all expected output filenames (based on the GeoJSON),
// verifies their existence and size, and logs missing or undersized files.
func checkDownloadedFiles(features []Feature, minFileSize int64, logPath string) error {
	logFile, err := os.Create(logPath)
	if err != nil {
		return fmt.Errorf("unable to create log file: %v", err)
	}
	defer logFile.Close()

	logger := log.New(logFile, "", log.LstdFlags)

	for _, feature := range features {
		filename := generateFilename(feature)

		info, err := os.Stat(filename)
		if os.IsNotExist(err) {
			logger.Printf("Missing file: %s\n", filename)
			continue
		}
		if err != nil {
			logger.Printf("Error accessing file %s: %v\n", filename, err)
			continue
		}
		if info.Size() < minFileSize {
			logger.Printf("File too small: %s (size: %d bytes), LinkData: %s\n", filename, info.Size(), feature.Properties.LinkData)
		}
	}

	return nil
}

// generateFilename builds the output file path for a given feature based on its Kachel and Datum.
func generateFilename(feature Feature) string {
	// Check if gOutputDir is a relative path, and resolve it to an absolute path if necessary
	absOutputDir, err := filepath.Abs(gOutputDir)
	if err != nil {
		fmt.Println("Error resolving output directory:", err)
		return ""
	}

	// Generate the filename using the resolved absolute path
	return filepath.Join(absOutputDir, fmt.Sprintf("dgm_%s_%s.xyz", feature.Properties.Kachel, feature.Properties.Datum))
}
