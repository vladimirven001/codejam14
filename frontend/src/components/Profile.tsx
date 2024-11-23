import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";

interface ProfileProps {
  onBack: () => void;
}

const Profile = ({ onBack }: ProfileProps) => {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-2xl font-bold">Account Settings</h2>
      </div>
      <Card className="p-6 space-y-6">
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input id="name" defaultValue="John Doe" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" defaultValue="john@example.com" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">New Password</Label>
          <Input id="password" type="password" />
        </div>
        <Button className="w-full">Save Changes</Button>
      </Card>
    </div>
  );
};

export default Profile;