package com.auradownloader.app

import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class MainActivityTest {

    @Test
    fun testActivityLaunch() {
        try {
            val activity = Robolectric.buildActivity(MainActivity::class.java).create().resume().get()
            println("Activity launched successfully!")
        } catch (e: Exception) {
            e.printStackTrace()
            throw e
        }
    }
}
