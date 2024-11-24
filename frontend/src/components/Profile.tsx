import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import { useState, useEffect } from "react";
import { useToast } from "@/components/ui/use-toast";
import Axios from "axios";

interface ProfileProps {
  onBack: () => void;
}

const Profile = ({ onBack }: ProfileProps) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    school: "",
    major: "",
  });
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    const userData = localStorage.getItem("currentUser");
    if (userData) {
      const user = JSON.parse(userData);
      setCurrentUser(user);
      setFormData({
        username: user.username || "",
        email: user.email || "",
        school: user.school || "",
        major: user.major || "",
      });
    }
  }, []);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id]: value
    }));
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const axiosClient = Axios.create({
        baseURL: "http://127.0.0.1:8000",
      });
      
      const response = await axiosClient.put('/users/' + currentUser.email, formData);
      
      // Merge the new form data with the current user data
      const updatedUser = {
        ...currentUser,
        ...formData
      };

      // Remove the password field from the updated user object
      delete updatedUser.password;

      // Save the updated user object without the password in local storage
      localStorage.setItem('currentUser', JSON.stringify(updatedUser));

      toast({
        title: "Profile updated successfully",
        description: "Your changes have been saved.",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error updating profile",
        description: "Please try again later.",
      });
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-2xl font-bold">Account Settings</h2>
      </div>
      <form onSubmit={handleSubmit}>
        <Card className="p-6 space-y-6">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input 
              id="username" 
              value={formData.username}
              onChange={handleChange}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input 
              id="email" 
              type="email" 
              value={formData.email}
              onChange={handleChange}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="school">School</Label>
            <Input 
              id="school" 
              value={formData.school}
              onChange={handleChange}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="major">Major</Label>
            <Input 
              id="major" 
              value={formData.major}
              onChange={handleChange}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">New Password</Label>
            <Input 
              id="password" 
              type="password"
              onChange={handleChange} 
            />
            <p className="text-sm text-muted-foreground">Leave blank to keep current password</p>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Saving..." : "Save Changes"}
          </Button>
        </Card>
      </form>
    </div>
  );
};

export default Profile;