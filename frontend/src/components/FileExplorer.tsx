import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FolderOpen, File, ChevronRight, ChevronDown, Folder, Minus } from "lucide-react";
import { Button } from "./ui/button";
import Axios from "axios";

interface File {
  name: string;
  size?: number; // Optional size for files if needed
}

interface Directory {
  id: string;
  name: string;
  files: File[];
  subdirectories: Directory[];
  isExpanded?: boolean;
}

interface FileExplorerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const FileExplorer = ({ open, onOpenChange }: FileExplorerProps) => {
  const [rootDirectory, setRootDirectory] = useState<Directory | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Recursive function to map directory
  const mapDirectory = (dir: any): Directory => ({
    id: dir.name,
    name: dir.name,
    files: dir.files || [],
    subdirectories: (dir.subdirectories || []).map(mapDirectory), // Recursively map subdirectories
    isExpanded: false, // Initialize with collapsed state
  });

  // Fetch user files from the backend
  const fetchUserFiles = async () => {
    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
      const userId = currentUser?.id;

      if (!userId) {
        throw new Error("No current user found.");
      }

      const axiosClient = Axios.create({
        baseURL: "http://127.0.0.1:8000",
      });

      const response = await axiosClient.get(`/users/${userId}/files`);
      const data = response.data;
      console.log(data);

      setRootDirectory(mapDirectory(data)); // Map the single root object
      setError(null);
    } catch (error: any) {
      if (Axios.isAxiosError(error) && error.response) {
        if (error.response.status === 404) {
          setError("No files found for the user.");
        } else {
          setError(`Error: ${error.response.statusText || "An unknown error occurred."}`);
        }
      } else {
        setError(error.message || "An unknown error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch files on component mount
  useEffect(() => {
    fetchUserFiles();
  }, []);

  // Toggle directory expansion
  const toggleDirectory = (directoryId: string) => {
    if (!rootDirectory) return;

    const updateDirectory = (dir: Directory): Directory => ({
      ...dir,
      isExpanded: dir.id === directoryId ? !dir.isExpanded : dir.isExpanded,
      subdirectories: dir.subdirectories.map(updateDirectory),
    });

    setRootDirectory(updateDirectory(rootDirectory));
  };

  const handleDropFile = (e: React.DragEvent, directoryId: string) => {
    e.preventDefault();
    e.stopPropagation();
  
    // Access the dropped files
    const droppedFiles = Array.from(e.dataTransfer.files);
  
    // Map the files to the `File` interface structure
    const newFiles: File[] = droppedFiles.map((file) => ({
      name: file.name,
      size: file.size,
    }));
  
    // Update the root directory to add the files to the specified directory
    if (!rootDirectory) return;
  
    const addFilesToDirectory = (dir: Directory): Directory => ({
      ...dir,
      files: dir.id === directoryId ? [...dir.files, ...newFiles] : dir.files,
      subdirectories: dir.subdirectories.map(addFilesToDirectory),
    });
  
    setRootDirectory(addFilesToDirectory(rootDirectory));
  };

  const handleDropFolder = (e: React.DragEvent, directioraryId: string) => {
    e.preventDefault();
    e.stopPropagation();

  };
  

const detectType = (e: React.DragEvent, directoryId: string) => {
  var items = [];
  for (var i = 0; i < e.dataTransfer.items.length; i++) {
      var item = e.dataTransfer.items[i];
      if (item.kind !== "file") continue;
      var entry = "getAsEntry" in DataTransferItem.prototype ? item.webkitGetAsEntry() : item.webkitGetAsEntry();
      if (entry.isDirectory){       
      console.log("this is a directory");
      console.log(directoryId)
      console.log(items[i])
      var numberValue = 0; // will return 0 if its a directiorary
      continue;}
      else{
        console.log("this is a file");
        return 1; // will return 1 if its a file
      }
  }
  return numberValue;
};


const detectTypeAndHandleFolder = async (e: React.DragEvent, directoryId: string) => {
  e.preventDefault();
  e.stopPropagation();

  for (let i = 0; i < e.dataTransfer.items.length; i++) {
    const item = e.dataTransfer.items[i];
    if (item.kind !== "file") continue;

    const entry =
      "getAsEntry" in DataTransferItem.prototype
        ? item.webkitGetAsEntry()
        : item.webkitGetAsEntry();

    if (!entry) continue;

    if (entry.isDirectory) {
      console.log("This is a directory:", entry.name);
      console.log("Directory ID:", directoryId);

      // Process the dropped folder and add it to the directory structure
      await addFolderToStructure(entry as FileSystemDirectoryEntry, directoryId);
    } else {
      console.log("This is a file:", entry.name);
    }
  }
};

// Function to add the folder and its contents to the directory structure
const addFolderToStructure = async (
  folderEntry: FileSystemDirectoryEntry,
  parentDirectoryId: string
) => {
  const reader = folderEntry.createReader();

  const readEntries = (): Promise<FileSystemEntry[]> =>
    new Promise((resolve, reject) => {
      reader.readEntries(resolve, reject);
    });

  let entries: FileSystemEntry[];

  // Prepare a new folder structure
  const newFolder: Directory = {
    id: `${parentDirectoryId}/${folderEntry.name}`,
    name: folderEntry.name,
    files: [],
    subdirectories: [],
    isExpanded: false,
  };

  try {
    do {
      entries = await readEntries();

      for (const entry of entries) {
        if (entry.isFile) {
          // If it's a file, add it to the new folder's files
          const fileEntry = entry as FileSystemFileEntry;
          const file = await new Promise<File>((resolve, reject) =>
            fileEntry.file(resolve, reject)
          );
          newFolder.files.push({ name: file.name, size: file.size });
        } else if (entry.isDirectory) {
          // If it's a subdirectory, process it recursively
          const subFolder = await addFolderToStructure(
            entry as FileSystemDirectoryEntry,
            newFolder.id
          );
          newFolder.subdirectories.push(subFolder);
        }
      }
    } while (entries.length > 0); // Continue until there are no more entries
  } catch (error) {
    console.error("Error reading directory:", error);
  }

  // Add the new folder to the directory structure
  if (!rootDirectory) return;

  const addFolderToDirectory = (dir: Directory): Directory => ({
    ...dir,
    subdirectories:
      dir.id === parentDirectoryId
        ? [...dir.subdirectories, newFolder]
        : dir.subdirectories.map(addFolderToDirectory),
  });

  setRootDirectory(addFolderToDirectory(rootDirectory));

  return newFolder; // Return the newly created folder for recursive use
};


// Recursively logs all files in a directory
const logDirectoryContents = async (directoryEntry: FileSystemDirectoryEntry) => {
  const reader = directoryEntry.createReader();

  const readEntries = (): Promise<FileSystemEntry[]> =>
    new Promise((resolve, reject) => {
      reader.readEntries(resolve, reject);
    });

  let entries: FileSystemEntry[];
  try {
    do {
      entries = await readEntries();

      for (const entry of entries) {
        if (entry.isFile) {
          const fileEntry = entry as FileSystemFileEntry;
          await logFile(fileEntry);
        } else if (entry.isDirectory) {
          console.log("Found subdirectory:", entry.name);
          await logDirectoryContents(entry as FileSystemDirectoryEntry); // Recursively process subdirectories
        }
      }
    } while (entries.length > 0); // Continue until there are no more entries
  } catch (error) {
    console.error("Error reading directory:", error);
  }
};

// Logs a single file entry
const logFile = async (fileEntry: FileSystemFileEntry) => {
  return new Promise<void>((resolve, reject) => {
    fileEntry.file(
      (file) => {
        console.log("File found:", file.name, `(${file.size} bytes)`);
        resolve();
      },
      (error) => reject(error)
    );
  });
};

// Function to delete the clicked file
const deleteFile = (fileId: string) => {
  if (!rootDirectory) return;

  const removeFile = (dir: Directory): Directory => ({
    ...dir,
    files: dir.files.filter((file) => file.name !== fileId),
    subdirectories: dir.subdirectories.map(removeFile),
  });

  setRootDirectory(removeFile(rootDirectory));
}

//Function to delete the clicked folder
const deleteFolder = (folderId: string) => {
  if (!rootDirectory) return;

  const removeFolder = (dir: Directory): Directory => ({
    ...dir,
    subdirectories: dir.subdirectories.filter((subdir) => subdir.id !== folderId),
  });

  setRootDirectory(removeFolder(rootDirectory));
}

  // Render directories recursively
  const renderDirectory = (directory: Directory, level = 0) => (
    <div key={directory.id}
    className="space-y-1"
    >
        <div
          className="flex items-center gap-2 p-2 hover:bg-accent rounded-md cursor-pointer"
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onDragOver={(e) => {
            e.preventDefault();
            e.currentTarget.classList.add("bg-blue-100");
            }}
            onDragLeave={(e) => {
              e.currentTarget.classList.remove("bg-blue-100");
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.stopPropagation();
              e.currentTarget.classList.remove("bg-blue-100");
              
              // Get the dropped items from the drag event
              const items = e.dataTransfer.items;
              const typeOfDraggedItem = detectType(e, directory.id);
              if (typeOfDraggedItem == 0) {
                console.log("we have a directoryyyyy");
                detectTypeAndHandleFolder(e, directory.id);
              }
              else{
                console.log("we have a fileeeee!");
                handleDropFile(e, directory.id)
              }
            }}
            >
          {/* <div className="items-center hover:bg-accent rounded-md cursor-pointer"> */}
            <Button onClick={() => toggleDirectory(directory.id)} variant="ghost" size="icon" className="h-7 w-7 p-0 hover:bg-green rounded-md cursor-pointer">
              {directory.isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
            <Folder onClick={() => toggleDirectory(directory.id)} className="h-4 w-4" />
            <span onClick={() => toggleDirectory(directory.id)} className="flex-grow">{directory.name}</span>
          {/* </div> */}
          { directory.name == "data" ? null :
            <Button onClick={() => deleteFolder(directory.name)} variant="destructive" size="icon" className="h-4 w-4 p-0 z-100">
              <Minus className="h-4 w-4" />
            </Button>
          }
        </div>
      {directory.isExpanded && (
        <>
          {directory.files.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 p-2 rounded-md"
              style={{ paddingLeft: `${(level + 1) * 16 + 8}px` }}
            >
              <File className="h-4 w-4" />
              <span className="flex-grow">{file.name}</span>
              <Button onClick={() => deleteFile(file.name)} variant="destructive" size="icon" className="h-4 w-4 p-0">
                <Minus className="h-4 w-4" />
              </Button>
            </div>
          ))}
          {directory.subdirectories.map((subdir) =>
            renderDirectory(subdir, level + 1) // Recursive call for subdirectories
          )}
        </>
      )}
    </div>
  );


  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>File Explorer</DialogTitle>
        </DialogHeader>
        <div className="min-h-[400px] border-2 border-dashed rounded-lg p-4">
          <ScrollArea className="h-[400px]">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <span>Loading files...</span>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center h-full text-red-500">
                <span>Error: {error}</span>
              </div>
            ) : !rootDirectory ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <FolderOpen className="h-12 w-12 mb-4" />
                <p>No files available</p>
              </div>
            ) : (
              renderDirectory(rootDirectory) // Render the single root directory
            )}
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default FileExplorer;
