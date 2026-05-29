import { useCallback, useEffect, useMemo, useState } from "react";
import { Bot, Plus, Save, Trash2 } from "lucide-react";
import { sparkyModelConfig } from "@/config";
import {
  createAgentProfile,
  deleteAgentProfile,
  deleteUserMemory,
  listAgentProfiles,
  listUserMemories,
  updateAgentProfile,
} from "@/services/agentProfilesService";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import "./ProfilesPage.css";

const emptyProfile = {
  name: "",
  system_prompt: "",
  default_model_id: sparkyModelConfig.defaultModelId || "",
  budget_level: 1,
  memory_policy: "project",
  enabled_tools: [],
  persona: "generic",
};

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [draft, setDraft] = useState(emptyProfile);
  const [memories, setMemories] = useState({ facts: [], preferences: [] });
  const [loading, setLoading] = useState(true);

  const selectedProfile = useMemo(
    () => {
      if (!selectedId || selectedId === "__new__") {
        return null;
      }
      return profiles.find((profile) => profile.profile_id === selectedId) || null;
    },
    [profiles, selectedId]
  );

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [profilesData, memoriesData] = await Promise.all([
        listAgentProfiles(),
        listUserMemories(),
      ]);
      const list = profilesData.profiles || [];
      setProfiles(list);
      setMemories({
        facts: memoriesData.facts || [],
        preferences: memoriesData.preferences || [],
      });
      if (!isCreating && !selectedId && list.length > 0) {
        setSelectedId(list[0].profile_id);
      }
    } catch (error) {
      toast.error(error.message || "Failed to load profiles");
    } finally {
      setLoading(false);
    }
  }, [selectedId, isCreating]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (isCreating || selectedId === "__new__") {
      return;
    }

    if (selectedProfile) {
      setDraft({ ...emptyProfile, ...selectedProfile });
    }
  }, [selectedProfile, selectedId, isCreating]);

  const startNew = () => {
    setSelectedId("__new__");
    setIsCreating(true);
    setDraft({
      ...emptyProfile,
      name: "",
      system_prompt: "",
      default_model_id: "amazon-nova-lite",
      budget_level: 1,
      memory_policy: "both",
      persona: "generic",
      enabled_tools: [],
    });
  };

  const saveProfile = async () => {
    try {
      const payload = {
        ...draft,
        budget_level: Number(draft.budget_level),
      };
      const data = !isCreating && selectedId && selectedId !== "__new__"
        ? await updateAgentProfile(selectedId, payload)
        : await createAgentProfile(payload);
      const saved = data.profile;
      setSelectedId(saved.profile_id);
      setIsCreating(false);
      await load();
      window.dispatchEvent(new CustomEvent("agentProfilesChanged"));
      toast.success("Profile saved");
    } catch (error) {
      toast.error(error.message || "Failed to save profile");
    }
  };

  const removeProfile = async () => {
    if (!selectedId) return;
    try {
      await deleteAgentProfile(selectedId);
      if (localStorage.getItem("selectedAgentProfileId") === selectedId) {
        localStorage.removeItem("selectedAgentProfileId");
        window.dispatchEvent(new CustomEvent("profileChanged", { detail: { profileId: "" } }));
      }
      setSelectedId("");
      setDraft(emptyProfile);
      await load();
      window.dispatchEvent(new CustomEvent("agentProfilesChanged"));
      toast.success("Profile deleted");
    } catch (error) {
      toast.error(error.message || "Failed to delete profile");
    }
  };

  const removeMemory = async (memoryRecordId) => {
    try {
      await deleteUserMemory(memoryRecordId);
      setMemories((prev) => ({
        facts: prev.facts.filter((m) => m.memory_record_id !== memoryRecordId),
        preferences: prev.preferences.filter((m) => m.memory_record_id !== memoryRecordId),
      }));
      toast.success("Memory deleted");
    } catch (error) {
      toast.error(error.message || "Failed to delete memory");
    }
  };

  return (
    <div className="profiles-page">
      <aside className="profiles-sidebar">
        <div className="profiles-sidebar-header">
          <h1>Profiles</h1>
          <Button size="sm" onClick={startNew}>
            <Plus className="size-4" />
            New
          </Button>
        </div>
        <div className="profiles-list">
          {profiles.map((profile) => (
            <button
              key={profile.profile_id}
              className={`profiles-list-item ${selectedId === profile.profile_id ? "active" : ""}`}
              onClick={() => { setSelectedId(profile.profile_id); setIsCreating(false); }}
            >
              <Bot className="size-4" />
              <span>{profile.name}</span>
            </button>
          ))}
          {!loading && profiles.length === 0 && (
            <p className="profiles-empty">No custom profiles yet.</p>
          )}
        </div>
      </aside>

      <main className="profiles-editor">
        <section className="profiles-section">
          <div className="profiles-section-header">
            <h2>{!isCreating && selectedId ? "Edit Profile" : "New Profile"}</h2>
            <div className="profiles-actions">
              {!isCreating && selectedId && selectedId !== "__new__" && (
                <Button variant="outline" onClick={removeProfile}>
                  <Trash2 className="size-4" />
                  Delete
                </Button>
              )}
              <Button onClick={saveProfile}>
                <Save className="size-4" />
                Save
              </Button>
            </div>
          </div>

          <label>
            Name
            <input
              value={draft.name}
              onChange={(e) => setDraft((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="Coding Partner"
            />
          </label>

          <label>
            Persona instructions
            <textarea
              value={draft.system_prompt}
              onChange={(e) => setDraft((prev) => ({ ...prev, system_prompt: e.target.value }))}
              placeholder="Describe how this profile should behave."
              rows={8}
            />
          </label>

          <div className="profiles-grid">
            <label>
              Default model
              <select
                value={draft.default_model_id || ""}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, default_model_id: e.target.value }))
                }
              >
                <option value="">Tokichan default</option>
                {sparkyModelConfig.models.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Budget
              <input
                type="number"
                min="0"
                max="4"
                value={draft.budget_level ?? 1}
                onChange={(e) => setDraft((prev) => ({ ...prev, budget_level: e.target.value }))}
              />
            </label>
            <label>
              Memory policy
              <select
                value={draft.memory_policy}
                onChange={(e) => setDraft((prev) => ({ ...prev, memory_policy: e.target.value }))}
              >
                <option value="off">Off</option>
                <option value="project">Project</option>
                <option value="global">Global</option>
                <option value="both">Both</option>
              </select>
            </label>
            <label>
              Persona key
              <input
                value={draft.persona || "generic"}
                onChange={(e) => setDraft((prev) => ({ ...prev, persona: e.target.value }))}
              />
            </label>
          </div>
        </section>

        <section className="profiles-section">
          <div className="profiles-section-header">
            <h2>Global Memory</h2>
          </div>
          <MemoryGroup title="Facts" items={memories.facts} onDelete={removeMemory} />
          <MemoryGroup title="Preferences" items={memories.preferences} onDelete={removeMemory} />
        </section>
      </main>
    </div>
  );
}

function MemoryGroup({ title, items, onDelete }) {
  return (
    <div className="profiles-memory-group">
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="profiles-empty">No {title.toLowerCase()} remembered.</p>
      ) : (
        <div className="profiles-memory-list">
          {items.map((item) => (
            <div key={item.memory_record_id} className="profiles-memory-item">
              <p>{item.content}</p>
              <button title="Delete memory" onClick={() => onDelete(item.memory_record_id)}>
                <Trash2 className="size-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
