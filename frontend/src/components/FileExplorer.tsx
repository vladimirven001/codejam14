import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FolderOpen, File, ChevronRight, ChevronDown, Folder } from "lucide-react";
import { useState } from "react";
import { Button } from "./ui/button";

interface FileExplorerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface Directory {
  id: string;
  name: string;
  files: File[];
  subdirectories: Directory[];
  isExpanded?: boolean;
}

const FileExplorer = ({ open, onOpenChange }: FileExplorerProps) => {
  const [directories, setDirectories] = useState<Directory[]>([
    {
      id: "1",
      name: "Documents",
      files: [],
      subdirectories: [
        {
          id: "2",
          name: "Projects",
          files: [],
          subdirectories: [],
        },
      ],
    },
    {
      id: "3",
      name: "Downloads",
      files: [],
      subdirectories: [],
    },
  ]);

  const handleDragOver = (e: React.DragEvent, directoryId: string) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent, directoryId: string) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFiles = Array.from(e.dataTransfer.files);
    
    setDirectories(prevDirs => {
      const updateDirectory = (dirs: Directory[]): Directory[] => {
        return dirs.map(dir => {
          if (dir.id === directoryId) {
            return {
              ...dir,
              files: [...dir.files, ...droppedFiles],
            };
          }
          if (dir.subdirectories.length > 0) {
            return {
              ...dir,
              subdirectories: updateDirectory(dir.subdirectories),
            };
          }
          return dir;
        });
      };
      return updateDirectory(prevDirs);
    });
  };

  const toggleDirectory = (directoryId: string) => {
    setDirectories(prevDirs => {
      const updateDirectory = (dirs: Directory[]): Directory[] => {
        return dirs.map(dir => {
          if (dir.id === directoryId) {
            return {
              ...dir,
              isExpanded: !dir.isExpanded,
            };
          }
          if (dir.subdirectories.length > 0) {
            return {
              ...dir,
              subdirectories: updateDirectory(dir.subdirectories),
            };
          }
          return dir;
        });
      };
      return updateDirectory(prevDirs);
    });
  };

  const renderDirectory = (directory: Directory, level = 0) => {
    return (
      <div key={directory.id} className="space-y-1">
        <div
          className="flex items-center gap-2 p-2 hover:bg-accent rounded-md cursor-pointer"
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => toggleDirectory(directory.id)}
          onDragOver={(e) => handleDragOver(e, directory.id)}
          onDrop={(e) => handleDrop(e, directory.id)}
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
                <span className="text-sm text-muted-foreground">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>
            ))}
            {directory.subdirectories.map(subdir => 
              renderDirectory(subdir, level + 1)
            )}
          </>
        )}
      </div>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>File Explorer</DialogTitle>
        </DialogHeader>
        <div className="min-h-[400px] border-2 border-dashed rounded-lg p-4">
          <ScrollArea className="h-[400px]">
            {directories.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <FolderOpen className="h-12 w-12 mb-4" />
                <p>Drag and drop files here</p>
              </div>
            ) : (
              <div className="space-y-2">
                {directories.map(dir => renderDirectory(dir))}
              </div>
            )}
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default FileExplorer;