package com.familytree.app

import android.content.ContentProvider
import android.content.ContentValues
import android.database.Cursor
import android.database.MatrixCursor
import android.net.Uri

/**
 * The birthdays, for the journal beside this app.
 *
 * UJournal keeps a calendar, and the birthdays the family already recorded here are the ones worth
 * having on it. A provider is the only way one app can read another's list: each app's files are its
 * own, and this hands over exactly what the reminder job already holds - the name of each living
 * person, the month and the day, and the year when one was given. No photo, no note, no date of
 * death, no address, and nothing about anyone the family did not give a birthday to.
 *
 * It is read-only by construction: [query] answers with one row holding that list as JSON, and every
 * write returns as if it did nothing, so a caller cannot change a single person through it. It is
 * exported because UJournal is a different app with a different signature; there is nothing here a
 * reader learns that the phone's own notification already says out loud.
 */
class BirthdayProvider : ContentProvider() {

    override fun onCreate(): Boolean = true

    override fun query(
        uri: Uri,
        projection: Array<out String>?,
        selection: String?,
        args: Array<out String>?,
        sort: String?
    ): Cursor {
        val ctx = context
        val json = if (ctx == null) "[]" else Birthdays.list(ctx)
        return MatrixCursor(COLUMNS).apply { addRow(arrayOf(json)) }
    }

    override fun getType(uri: Uri): String = "application/json"

    // Nothing can be written through this provider: it exists to be read.
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null

    override fun delete(uri: Uri, selection: String?, args: Array<out String>?): Int = 0

    override fun update(uri: Uri, values: ContentValues?, selection: String?, args: Array<out String>?): Int = 0

    private companion object {
        val COLUMNS = arrayOf("json")
    }
}
