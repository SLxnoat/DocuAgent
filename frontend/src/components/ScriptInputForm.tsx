import * as React from "react";
import { useManualStore } from "@/store/useManualStore";
import { generateManual } from "@/api/client";

export function ScriptInputForm() {
  const { setJobId, setSessionId, setJobStatus, setMarkdownContent, reset } =
    useManualStore();

  const [script, setScript] = React.useState("");
  const [url, setUrl] = React.useState("");
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [formErrors, setFormErrors] = React.useState<{
    script?: string;
    url?: string;
    username?: string;
    password?: string;
    general?: string;
  }>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Reset errors
    setFormErrors({});

    // Validate form
    let isValid = true;
    const errors: typeof formErrors = {};

    if (!script || script.trim().length < 10) {
      errors.script = "Script must be at least 10 characters long";
      isValid = false;
    }

    if (!url) {
      errors.url = "URL is required";
      isValid = false;
    } else {
      try {
        new URL(url);
      } catch {
        errors.url = "Please enter a valid URL";
        isValid = false;
      }
    }

    // Note: Credentials are optional based on the API spec

    if (!isValid) {
      setFormErrors(errors);
      return;
    }

    // Set submitting state
    setIsSubmitting(true);
    setJobStatus("queued");

    try {
      // Call the API to generate manual
      const response = await generateManual({
        script: script.trim(),
        target_url: url,
        credentials: {
          username: username || undefined,
          password: password || undefined,
        },
      });

      // Store the IDs from the response
      setJobId(response.job_id);
      setSessionId(response.session_id);
      setJobStatus("analyzing"); // Next step after queued
    } catch (error: any) {
      // Handle error
      console.error("Failed to submit form:", error);
      setFormErrors({
        general: error.message || "Failed to submit form. Please try again.",
      });
      setJobStatus("failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle credential field changes with immediate sanitization
  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value);
    // Note: We don't clear the value here as the user might still be typing
    // The clearing will happen after form submission or reset
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    // Same as above - we'll clear after submission
  };

  // Clear sensitive data after form submission
  React.useEffect(() => {
    if (!isSubmitting) {
      // Clear credential fields after submission attempt
      // This ensures credentials don't linger in React state
      setUsername("");
      setPassword("");
    }
  }, [isSubmitting]);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Workflow Script
        </label>
        <textarea
          value={script}
          onChange={(e) => setScript(e.target.value)}
          placeholder="Describe the workflow steps you want to document (minimum 10 characters)..."
          rows={8}
          className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
            formErrors.script ? "border-red-500" : ""
          }`}
        />
        {formErrors.script && (
          <p className="mt-1 text-sm text-red-600">{formErrors.script}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Staging URL
        </label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://your-staging-app.example.com"
          className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
            formErrors.url ? "border-red-500" : ""
          }`}
        />
        {formErrors.url && (
          <p className="mt-1 text-sm text-red-600">{formErrors.url}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Username (Optional)
          </label>
          <input
            type="text"
            value={username}
            onChange={handleUsernameChange}
            placeholder="Enter username for authentication"
            className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
              formErrors.username ? "border-red-500" : ""
            }`}
          />
          {formErrors.username && (
            <p className="mt-1 text-sm text-red-600">{formErrors.username}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Password (Optional)
          </label>
          <input
            type="password"
            value={password}
            onChange={handlePasswordChange}
            placeholder="Enter password for authentication"
            className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
              formErrors.password ? "border-red-500" : ""
            }`}
          />
          {formErrors.password && (
            <p className="mt-1 text-sm text-red-600">{formErrors.password}</p>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <button
          type="submit"
          disabled={isSubmitting}
          className={`flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 ${
            isSubmitting ? "cursor-not-allowed" : ""
          }`}
        >
          {isSubmitting ? "Generating..." : "Generate Manual"}
        </button>

        <button
          type="button"
          onClick={() => {
            setScript("");
            setUrl("");
            setUsername("");
            setPassword("");
            setFormErrors({});
            reset(); // Reset the store
          }}
          className="ml-4 bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          Clear Form
        </button>
      </div>
    </form>
  );
}
