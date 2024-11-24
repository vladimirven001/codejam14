import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, User, LogOut } from "lucide-react";
import FileExplorer from "@/components/FileExplorer";
import Profile from "@/components/Profile";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Axios from "axios";
import { set } from "date-fns";
import { useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
}

interface ChatHistory {
  id: string;
  title: string;
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [input, setInput] = useState("");
  const [showFileExplorer, setShowFileExplorer] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const [profilePicture, setProfilePicture] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    navigate('/auth/login');
  };

  useEffect(() => {
    // Get the profile picture URL from localStorage
    const user = localStorage.getItem('currentUser');
    if (user) {
      const userData = JSON.parse(user);
      console.log("User Data:", userData);
      setProfilePicture(userData.profilePicture);
    }
  } , []);

    useEffect(() => {
      if (profilePicture) {
        // Get Profile Picture from server
        const axiosClient = Axios.create({
          baseURL: "http://127.0.0.1:8000",
          responseType: 'arraybuffer', // Ensure we get the image as an array buffer
        });
  
        console.log("Fetching Profile Picture:", profilePicture);
  
        const fetchProfilePicture = async () => {
          try {
            // const response = await axiosClient.get("/images/" + profilePicture, {
            //   responseType: 'blob', // Ensure we get the image as a blob
            // });

            const response = await axiosClient.get("/images/" + profilePicture);
            console.log("Response:", response);

            // Ensure the response is successful
            if (response.status !== 200) {
              throw new Error('Failed to fetch file');
            }

            // Create blob from array buffer
            const blob = new Blob([response.data], { type: 'image/jpeg' });

            // Create object URL from blob
            const imageUrl = URL.createObjectURL(blob);
            console.log("Successfully created image URL:", imageUrl);
            setImageUrl(imageUrl);
          } catch (error) {
            console.error("Error fetching profile picture:", error);
          }
        };
  
        fetchProfilePicture(); // Call the async function to fetch the image
      }
    }, [profilePicture]); // Depend on profilePicture so it triggers when it changes
  
  const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
  const userId = currentUser?.id;

  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const axiosClient = Axios.create({
          baseURL: "http://127.0.0.1:8000",
        });
        const response = await axiosClient.get(`/users/${userId}/conversations`);
        if (response.status === 200) {
          const data = response.data;
          const formattedChatHistory = data.conversations.map((conversation: any) => ({
            id: conversation.id.toString(),
            title: new Date(conversation.time).toLocaleString(), // Convert time to readable string
          }));
          setChatHistory(formattedChatHistory);
        } else if (response.status === 404) {
          console.log("No chat history found.");
        } else {
          console.error("Failed to fetch chat history:", response.data);
        }
      } catch (error) {
        console.error("Error fetching chat history:", error);
      }
    };

    fetchChatHistory();
  }, [userId]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      isUser: true,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // TODO: Implement actual AI response logic
    const aiResponse: Message = {
      id: (Date.now() + 1).toString(),
      content: "This is a placeholder response. AI integration coming soon!",
      isUser: false,
    };

    setMessages((prev) => [...prev, aiResponse]);
  };

  const handleNewConversation = async () => {
    try {
      const axiosClient = Axios.create({
        baseURL: "http://127.0.0.1:8000",
      });
      const response = await axiosClient.post(`/users/${userId}/conversations`);
      if (response.status === 201) {
        const newConversation = response.data.conversation;
        setChatHistory((prev) => [
          ...prev,
          {
            id: newConversation.id.toString(),
            title: new Date(newConversation.time).toLocaleString(),
          },
        ]);
      } else {
        console.error("Failed to create a new conversation:", response.data);
      }
    } catch (error) {
      console.error("Error creating a new conversation:", error);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Left Sidebar */}
      <div className="w-64 border-r flex flex-col">
        <div className="p-4 border-b">
          <Button
            variant="outline"
            className="w-full flex items-center gap-2 mt-2"
            onClick={() => setShowFileExplorer(true)}
          >
            <Plus className="h-4 w-4" />
            Add Files
          </Button>
        </div>
        <div className="p-4">
          <h3 className="text-lg font-bold">Conversations</h3>
          <Button
            variant="outline"
            className="w-full flex items-center gap-2 mt-2"
            onClick={handleNewConversation}
          >
            <Plus className="h-4 w-4" />
            New Conversation
        </Button>
        </div>
        <ScrollArea className="flex-grow">
          <div className="p-2 space-y-2">
            {chatHistory.map((chat) => (
              <Button
                key={chat.id}
                variant="ghost"
                className="w-full justify-start text-sm font-normal"
              >
                {chat.title}
              </Button>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="h-16 border-b flex items-center justify-end px-4">
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon"
                className="relative"
              >
                <Avatar>
                  <AvatarImage src={imageUrl} />
                  <AvatarFallback>
                    <User className="h-5 w-5" />
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setShowProfile(!showProfile)}>
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Content Area */}
        {showProfile ? (
          <Profile onBack={() => setShowProfile(false)} />
        ) : (
          <>
            {/* Chat Messages */}
            <div className="flex-grow overflow-auto p-4">
              <ScrollArea className="h-full">
                <div className="space-y-4 max-w-3xl mx-auto">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.isUser ? "justify-end" : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.isUser
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                      >
                        {message.content}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>

            {/* Input Area */}
            <div className="border-t p-4">
              <form onSubmit={handleSend} className="max-w-3xl mx-auto">
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question about your notes..."
                    className="flex-grow"
                  />
                  <Button type="submit">Send</Button>
                </div>
              </form>
            </div>
          </>
        )}
      </div>

      <FileExplorer
        open={showFileExplorer}
        onOpenChange={setShowFileExplorer}
      />
    </div>
  );
};

export default Chat;
