package com.familytree.app

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import org.json.JSONArray
import java.util.Calendar
import java.util.concurrent.TimeUnit

// Birthday reminders. The page knows who is alive and when they were born; only the day and month of
// each living person is kept here, so the same date comes round on its own every year and nothing has
// to be sent again. A daily job wakes shortly after nine in the morning and, when it is someone's
// birthday today, puts one quiet notification on the phone — whether the app is open or not.
object Birthdays {
    private const val PREFS = "familytree.bdays"
    private const val KEY_ON = "on"
    private const val KEY_LIST = "list"
    private const val CHANNEL = "birthdays"
    private const val UNIQUE = "birthday-reminders"
    private const val HOUR = 9

    private fun prefs(c: Context) = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun isOn(c: Context) = prefs(c).getBoolean(KEY_ON, false)

    // the page's list: [{"n":name,"m":month,"d":day,"y":year}], year 0 when it was never given
    fun save(c: Context, json: String) = prefs(c).edit().putString(KEY_LIST, json).apply()

    fun set(c: Context, on: Boolean) {
        prefs(c).edit().putBoolean(KEY_ON, on).apply()
        if (on) schedule(c) else WorkManager.getInstance(c).cancelUniqueWork(UNIQUE)
    }

    // one check a day, first one at nine in the morning and every day after that
    fun schedule(c: Context) {
        val now = Calendar.getInstance()
        val next = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, HOUR); set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0); set(Calendar.MILLISECOND, 0)
            if (!after(now)) add(Calendar.DAY_OF_YEAR, 1)
        }
        val r = PeriodicWorkRequestBuilder<BirthdayWorker>(1, TimeUnit.DAYS)
            .setInitialDelay(next.timeInMillis - now.timeInMillis, TimeUnit.MILLISECONDS).build()
        WorkManager.getInstance(c).enqueueUniquePeriodicWork(UNIQUE, ExistingPeriodicWorkPolicy.UPDATE, r)
    }

    fun notifyToday(c: Context) {
        if (!isOn(c)) return
        val nm = NotificationManagerCompat.from(c)
        if (!nm.areNotificationsEnabled()) return
        val today = Calendar.getInstance()
        val mo = today.get(Calendar.MONTH) + 1
        val day = today.get(Calendar.DAY_OF_MONTH)
        val list = try { JSONArray(prefs(c).getString(KEY_LIST, "[]")) } catch (e: Exception) { JSONArray() }
        val open = PendingIntent.getActivity(c, 0, Intent(c, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        for (i in 0 until list.length()) {
            val o = list.optJSONObject(i) ?: continue
            if (o.optInt("m") != mo || o.optInt("d") != day) continue
            val name = o.optString("n").ifBlank { "Someone in your family" }
            val y = o.optInt("y")
            val age = if (y in 1 until today.get(Calendar.YEAR)) today.get(Calendar.YEAR) - y else 0
            channel(c)
            val note = NotificationCompat.Builder(c, CHANNEL)
                .setSmallIcon(R.drawable.ic_launcher)
                .setContentTitle("🎂 $name’s birthday")
                .setContentText(if (age > 0) "Turning $age today – from your family tree" else "From your family tree")
                .setContentIntent(open).setAutoCancel(true).build()
            try { nm.notify(1000 + i, note) } catch (e: SecurityException) { return }   // not allowed: say nothing
        }
    }

    private fun channel(c: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val m = c.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (m.getNotificationChannel(CHANNEL) == null)
            m.createNotificationChannel(NotificationChannel(CHANNEL, "Birthdays", NotificationManager.IMPORTANCE_DEFAULT).apply {
                description = "A reminder on each living person’s birthday"
            })
    }
}

class BirthdayWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result {
        Birthdays.notifyToday(applicationContext)
        return Result.success()
    }
}
