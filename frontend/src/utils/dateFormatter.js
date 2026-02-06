/**
 * Convert backend date string to UTC date object
 * Backend format: "2026-02-08T19:10:47.948304" (missing Z suffix)
 * @param {string} dateString - Date string from API (UTC but without Z)
 * @returns {Date} Date object in UTC
 */
const parseBackendDate = (dateString) => {
  if (!dateString) return null;
  // Add 'Z' to mark as UTC if not already present
  const dateWithZ = dateString.includes("Z") ? dateString : `${dateString}Z`;
  return new Date(dateWithZ);
};

/**
 * Format a date with time in local timezone
 * @param {string} dateString - ISO date string from API (UTC)
 * @returns {string} Formatted date with time (e.g., "09 Feb 2026, 02:30 PM")
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return "";
  try {
    const utcDate = parseBackendDate(dateString);
    if (!utcDate || isNaN(utcDate.getTime())) return dateString;
    
    return new Intl.DateTimeFormat("en-US", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    }).format(utcDate);
  } catch (error) {
    console.error("Error formatting date with time:", error);
    return dateString;
  }
};
