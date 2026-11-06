package com.familytree.app

import android.content.Context
import android.net.Uri
import org.json.JSONArray
import org.json.JSONObject

/**
 * The birthdays UJournal keeps, read through the read-only provider it publishes at
 * `content://app.ujournal.birthdays/list`.
 *
 * The journal hands over the same short list this app hands to it - a name, a month and a day for
 * each birthday it holds, plus the year when one was given - in exactly the shape [BirthdayProvider]
 * answers with, so one reader of either is the same code. It answers a query and refuses every
 * write, so this is a read and nothing more: nothing here can add, change or remove a birthday in
 * the journal.
 *
 * Everything fails quietly. The journal may not be installed, may be older than its provider, or may
 * have no birthdays in it; each of those is an empty list, which is what the page draws.
 */
object JournalBirthdays {

    private val URI: Uri = Uri.parse("content://app.ujournal.birthdays/list")

    /**
     * The journal's birthdays as `[{"n":name,"m":month,"d":day,"y":year}]`, already checked: a row
     * with no name or no real day is dropped rather than drawn as a blank one.
     */
    fun list(ctx: Context): String = try {
        val raw = ctx.contentResolver.query(URI, null, null, null, null)?.use { cur ->
            if (!cur.moveToFirst()) null else {
                val i = cur.getColumnIndex("json")
                if (i < 0) null else cur.getString(i)
            }
        } ?: "[]"
        val arr = JSONArray(raw)
        val out = JSONArray()
        for (k in 0 until arr.length()) {
            val o = arr.optJSONObject(k) ?: continue
            val name = o.optString("n").trim().take(80)
            val m = o.optInt("m")
            val d = o.optInt("d")
            if (name.isEmpty() || m !in 1..12 || d !in 1..31) continue
            out.put(
                JSONObject()
                    .put("n", name)
                    .put("m", m)
                    .put("d", d)
                    .put("y", o.optInt("y"))
            )
        }
        out.toString()
    } catch (e: Exception) {
        "[]"
    }
}
