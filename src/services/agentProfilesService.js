import { getAuthToken } from "../components/Agent/context/utils";
import {
  CORE_SERVICES_ENDPOINT,
  CORE_SERVICES_SESSION_ID,
} from "../components/Agent/context/constants";
import { createSparkySessionHeader } from "../utils/sessionSeed";

const request = async (input) => {
  const token = await getAuthToken();
  const response = await fetch(CORE_SERVICES_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id":
        createSparkySessionHeader(CORE_SERVICES_SESSION_ID),
    },
    body: JSON.stringify({ input }),
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const data = await response.json();
  if (data.type === "error") {
    const err = new Error(data.message || "Request failed");
    err.code = data.error_code;
    err.details = data.details;
    throw err;
  }
  return data;
};

export const listAgentProfiles = () => request({ type: "list_agent_profiles" });

export const createAgentProfile = (profile) => request({ type: "create_agent_profile", profile });

export const updateAgentProfile = (profileId, profile) =>
  request({ type: "update_agent_profile", profile_id: profileId, profile });

export const deleteAgentProfile = (profileId) =>
  request({ type: "delete_agent_profile", profile_id: profileId });

export const listUserMemories = () => request({ type: "list_user_memories" });

export const deleteUserMemory = (memoryRecordId) =>
  request({ type: "delete_user_memory", memory_record_id: memoryRecordId });
