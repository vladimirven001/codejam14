import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FolderOpen, File, ChevronRight, ChevronDown, Folder } from "lucide-react";
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

  // Render directories recursively
  const renderDirectory = (directory: Directory, level = 0) => (
    <div key={directory.id} className="space-y-1">
      <div
        className="flex items-center gap-2 p-2 hover:bg-accent rounded-md cursor-pointer"
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => toggleDirectory(directory.id)}
      >
        <Button variant="ghost" size="icon" className="h-4 w-4 p-0">
          {directory.isExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
        <Folder className="h-4 w-4" />
        <span className="flex-grow">{directory.name}</span>
      </div>
      {directory.isExpanded && (
        <>
          {directory.files.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 p-2 hover:bg-accent rounded-md"
              style={{ paddingLeft: `${(level + 1) * 16 + 8}px` }}
            >
              <File className="h-4 w-4" />
              <span className="flex-grow">{file.name}</span>
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
