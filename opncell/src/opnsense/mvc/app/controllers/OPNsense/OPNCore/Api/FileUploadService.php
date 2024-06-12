<?php

namespace OPNsense\OPNCore\Api;

class FileUploadService
{

    public function processFile($file): array
    {
        $handle = fopen($file["tmp_name"], "r");
        if ($file["type"] === "text/csv") {
            return $this->processCSVFile($handle);
        } else {
            return $this->processInpOutFiles($handle);
        }
    }

    public function headersToLowerCase($headers)
    {
        $i=0;
        foreach ($headers as $item) {
            $headers[$i] = strtolower($item);
            $i++;
        }
        return $headers;
    }
    public function processInpOutFiles($handle): array
    {
        $foundStart = false;
        $headers = array();
        $isOutFile = false;
        $contentLines = array();

        $counter = 0;
        while (($line = fgets($handle)) !== false) {
            if (empty(trim($line))) { // ignore empty lines
                continue;
            }
            $counter +=1;
            // Check if the line starts with "var_out:"
            if (strpos($line, "var_out:") === 0) {
                $foundStart = true;
                if ($counter === 1) { // if var_out: is on the very first line it is an outfile
                    $isOutFile = true;
                }
                $line = str_replace("var_out:", "", $line);
                $headers = explode("/", trim($line));
                $headers = $this->headersToLowerCase($headers);
            }
            if ($foundStart) {
                // Split the line by tabs or multiple spaces if inp file and by comma if outfile
                if ($isOutFile) {
                    $record = explode(",", trim($line));
                } else {
                    $record = preg_split('/\t+|\s{2,}/', trim($line));
                }
                // Check if the number of elements in $headers matches the number of elements
                // in $record (for empty rows)
                if (count($headers) == count($record)) {
                    // Map the values to keys from headers array
                    $mappedRecord = array_combine($headers, $record);
                    $contentLines[] = $mappedRecord;
                }
            }
        }
        session_start();
        $_SESSION['fileValues'] = $contentLines;
        fclose($handle);
        return $contentLines;
    }

    public function processCSVFile($handle): array
    {
        $headers = fgetcsv($handle);
        $headers = $this->headersToLowerCase($headers);
        $data = array();
        while (($row = fgetcsv($handle)) !== false) {
            $row = array_combine($headers, $row);
            $data[] = $row;
            while (($row = fgetcsv($handle)) !== false) {
                $row = array_combine($headers, $row);
                $data[] = $row;
            }
        }
        session_start();
        $_SESSION['fileValues'] = $data;
        fclose($handle);
        return $data;
    }
}