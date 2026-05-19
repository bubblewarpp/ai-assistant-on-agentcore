import { useCallback, useEffect, useState } from "react";
import { Bot, Check, ChevronsUpDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { listAgentProfiles } from "@/services/agentProfilesService";

const PROFILE_STORAGE_KEY = "selectedAgentProfileId";

export const getSelectedProfileId = () => {
  return localStorage.getItem(PROFILE_STORAGE_KEY) || "";
};

const DEFAULT_PROFILE = {
  profile_id: "",
  name: "Sparky Default",
};

export default function ProfileSelector({ compact = false }) {
  const [profiles, setProfiles] = useState([DEFAULT_PROFILE]);
  const [selectedId, setSelectedId] = useState(getSelectedProfileId());

  const loadProfiles = useCallback(async () => {
    try {
      const data = await listAgentProfiles();
      setProfiles([DEFAULT_PROFILE, ...(data.profiles || [])]);
    } catch {
      setProfiles([DEFAULT_PROFILE]);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    listAgentProfiles()
      .then((data) => {
        if (cancelled) return;
        setProfiles([DEFAULT_PROFILE, ...(data.profiles || [])]);
      })
      .catch(() => setProfiles([DEFAULT_PROFILE]));
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const handler = () => setSelectedId(getSelectedProfileId());
    const profilesHandler = () => {
      setSelectedId(getSelectedProfileId());
      loadProfiles();
    };
    window.addEventListener("profileChanged", handler);
    window.addEventListener("agentProfilesChanged", profilesHandler);
    return () => {
      window.removeEventListener("profileChanged", handler);
      window.removeEventListener("agentProfilesChanged", profilesHandler);
    };
  }, [loadProfiles]);

  const selected = profiles.find((p) => p.profile_id === selectedId) || DEFAULT_PROFILE;

  const handleSelect = (profile) => {
    setSelectedId(profile.profile_id);
    if (profile.profile_id) {
      localStorage.setItem(PROFILE_STORAGE_KEY, profile.profile_id);
    } else {
      localStorage.removeItem(PROFILE_STORAGE_KEY);
    }
    window.dispatchEvent(
      new CustomEvent("profileChanged", { detail: { profileId: profile.profile_id } })
    );
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size={compact ? "sm" : "default"} className="gap-2">
          <Bot className="size-4" />
          <span className="max-w-40 truncate">{selected.name}</span>
          <ChevronsUpDown className="size-4 opacity-70" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="min-w-60" align="start">
        <DropdownMenuLabel className="text-xs text-muted-foreground">
          Choose profile
        </DropdownMenuLabel>
        <DropdownMenuGroup>
          {profiles.map((profile) => (
            <DropdownMenuItem
              key={profile.profile_id || "default"}
              onClick={() => handleSelect(profile)}
              className="cursor-pointer"
            >
              <span>{profile.name}</span>
              {selected.profile_id === profile.profile_id && <Check className="ml-auto size-4" />}
            </DropdownMenuItem>
          ))}
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
