#!/bin/bash
# פותח את Google Chrome בפרופילים שונים, כל פרופיל עם רשימת אתרים משלו.
# מקור הנתונים: כל קובץ .txt בתיקייה profiles/
# בכל קובץ - שורה ראשונה # PROFILE=<שם תיקיית פרופיל>, ואז שורה אחת לכל URL.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILES_DIR="$DIR/profiles"
LOG="$DIR/run.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === starting morning chrome ===" >> "$LOG"

# עוברים על קבצי הפרופילים לפי סדר אלפבתי (01-, 02-, ...)
for file in "$PROFILES_DIR"/*.txt; do
  [ -f "$file" ] || continue

  profile=""
  urls=()

  while IFS= read -r line || [ -n "$line" ]; do
    trimmed="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [ -z "$trimmed" ] && continue

    # שורת הגדרת פרופיל: # PROFILE=Profile 1
    if [[ "$trimmed" =~ ^#[[:space:]]*PROFILE[[:space:]]*= ]]; then
      profile="$(echo "$trimmed" | sed 's/^#[[:space:]]*PROFILE[[:space:]]*=[[:space:]]*//')"
      continue
    fi

    # שורות הערה רגילות - דלג
    case "$trimmed" in \#*) continue ;; esac

    urls+=("$trimmed")
  done < "$file"

  fname="$(basename "$file")"

  if [ -z "$profile" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SKIP $fname - no PROFILE directive" >> "$LOG"
    continue
  fi

  if [ ${#urls[@]} -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SKIP $fname - no urls" >> "$LOG"
    continue
  fi

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] opening $fname → profile=\"$profile\" (${#urls[@]} urls)" >> "$LOG"

  # פתיחה ישירה דרך הבינארי של Chrome - מאפשרת לפתוח חלון חדש לכל פרופיל
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
      --profile-directory="$profile" "${urls[@]}" \
      >> "$LOG" 2>&1 &

  # השהיה קצרה כדי שכרום יספיק לפתוח חלון לפני שאנחנו פותחים את הבא
  sleep 2
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === done ===" >> "$LOG"
